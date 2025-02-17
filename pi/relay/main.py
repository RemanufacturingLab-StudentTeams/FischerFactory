import asyncio
from asyncio import run_coroutine_threadsafe, Future
import json
from asyncua import Node, ua
from asyncua import Client as OPCUAClient
from asyncua.ua.uaerrors import BadTooManySubscriptions
from asyncua.client.client import Subscription
from paho.mqtt import client as mqtt_client
from paho.mqtt.client import Client as MqttClient
from dotenv import load_dotenv
import os, argparse
import pprint
from mappings import mappings, special_rules
from datetime import datetime
from helper import get_children_fast, get_display_name_fast, name_to_mqtt, value_to_ua, get_datatype_as_str
from opcua_datachange_handler import LeafDataChangeHandler, FieldDataChangeHandler
from typing import Optional
from state import push_mqtt, send_response
from common import MqttClient, singleton, RuntimeManager, setup
import atexit

# Load environment variables
os.environ.clear()

load_dotenv(dotenv_path=f".env")
print(f"Running with environment variables:")
pprint.pprint(os.environ.copy())
setup()

import logging

PLC_IP = os.getenv('PLC_IP')
PLC_PORT = int(os.getenv('PLC_PORT'))
MQTT_BROKER_IP = os.getenv('MQTT_BROKER_IP')
MQTT_BROKER_PORT = int(os.getenv('MQTT_BROKER_PORT'))
MQTT_USERNAME = os.getenv('MQTT_USERNAME')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')

opcua_clients: list[OPCUAClient] = []
async def add_opcua_client():
    new_client = OPCUAClient(f"opc.tcp://{PLC_IP}:{PLC_PORT}")
    opcua_clients.append(new_client)
    async def connect_opcua(opcua_client: OPCUAClient):
        try:
            await opcua_client.connect()
            logging.info(f'Connected to PLC OPCUA server at <{PLC_IP}:{PLC_PORT}>')
        except Exception as e:
            logging.warning(f'Failed to connect to PLC at <{PLC_IP}:{PLC_PORT}>: {e}')
            logging.warning('Retrying in a second...')
            await asyncio.sleep(1)
            await connect_opcua(opcua_client)
    await connect_opcua(new_client)
    await new_client.load_data_type_definitions() # load custom types
    
async def disconnect_opcua_clients():
    coros = [c.close_session() for c in opcua_clients]
    await asyncio.gather(*coros)
    
def disconnect_opcua_clients_sync():
    asyncio.run(disconnect_opcua_clients())
    
atexit.register(disconnect_opcua_clients_sync)

async def opcua_create_subscription_safe(handler: LeafDataChangeHandler | FieldDataChangeHandler) -> Subscription:
    try:
        return await opcua_clients[-1].create_subscription(period=1000, handler=handler)
    except BadTooManySubscriptions:
        logging.warning('OPCUA Client has too many subscriptions, making another one...')
        await add_opcua_client()
        return await opcua_clients[-1].create_subscription(period=1000, handler=handler)

async def relay_opcua_to_mqtt(opcua_clients: list[OPCUAClient]):
    mqtt_client = MqttClient()
    async def subscribe_recursive(node: Node, base_topic: str, EXCLUDE:Optional[list[str]]=None):
        node_name = (await get_display_name_fast(node)).Text
        logging.info(f"[MQTT_RELAY] Recursively subscribing to '{node_name}', mapping to topic '{base_topic}'")
        children = await get_children_fast(node)
        has_grandchildren = len(await get_children_fast(children[0])) != 0
        if not has_grandchildren:  # Leaf node, children is payload
            logging.debug(f'[OPCUA->MQTT] Node {node_name} is leaf')
            if (await node.read_node_class()) == 2: 
                handler = LeafDataChangeHandler(mqtt_client, base_topic, EXCLUDE=EXCLUDE)
                subscription = await opcua_create_subscription_safe(handler)
                await subscription.subscribe_data_change(node)
                
            else: # Sometimes a leaf node is not a UAVariable type, which means it cannot be subscribed to. In this case, subscribe to the fields individually 
                for field in (await get_children_fast(node)):
                    field_name = (await get_display_name_fast(field)).Text
                    logging.debug(f'[OPCUA->MQTT] Found independent field {field_name}')
                    if EXCLUDE:
                        if (field_name) in EXCLUDE:
                            logging.debug(f'[OPCUA->MQTT] Skipping explicitly excluded field {field_name}')
                            continue
                    handler = FieldDataChangeHandler(mqtt_client, base_topic)
                    subscription = await opcua_create_subscription_safe(handler)
                    await subscription.subscribe_data_change(field)
        else:  # Non-leaf node (i.e., it has grandchildren), recurse
            for child in children:
                child_name = (await get_display_name_fast(child)).Text
                logging.debug(f'[OPCUA->MQTT] Found child {child_name}')
                if EXCLUDE:
                    if child_name in EXCLUDE:
                        logging.debug(f'[OPCUA->MQTT] Skipping explicitly excluded child {child_name}')
                        continue
                if not child_name:
                    raise ValueError(f'[OPCUA->MQTT] Child {child} has no display name.')
                mqtt_sub_topic = f"{base_topic}/{name_to_mqtt(child_name)}"
                logging.debug(f'[OPCUA->MQTT] Generated subtopic: {mqtt_sub_topic} from {child_name}')
                await subscribe_recursive(child, mqtt_sub_topic, EXCLUDE=EXCLUDE)

    async with opcua_clients[-1] as opcua_client:
        for mapping in mappings:
            logging.debug(f'[OPCUA->MQTT] Mapping {mapping.FROM} to {mapping.TO}')
            if mapping.FROM.startswith('"'):  # OPC UA -> MQTT
                root_node: Node = opcua_client.get_node('ns=3;s=' + mapping.FROM)
                base_topic = mapping.TO
                await subscribe_recursive(root_node, base_topic, EXCLUDE=mapping.EXCLUDE)
        await asyncio.Future()

async def relay_mqtt_to_opcua(opcua_client: OPCUAClient):
    mqtt_client = MqttClient()
    for mapping in mappings:
        topic = mapping.FROM
        leaf_node_id = 'ns=3;s=' + mapping.TO
        logging.info(f'[MQTT->OPCUA] Mapping {topic} to {leaf_node_id}')
        
        async def send_to_opcua(payload, opcua_client=opcua_client, node_id=leaf_node_id, topic=topic) -> None:
            try:
                logging.debug(f'[MQTT->OPCUA] Received payload {payload}: {type(payload)} on topic {topic}')
                node = opcua_client.get_node(nodeid=node_id)
                
                if not isinstance(payload, dict):
                    logging.warning(f'Payload of topic {topic} was expected to be a dict, but it was {type(payload)}')
                    await node.write_value(value_to_ua(payload, (await get_datatype_as_str(node))))
                    logging.info(f'[MQTT->OPCUA] Sent single value {payload} to OPCUA.')
                    send_response(topic=topic, message=f'Sent value {payload} to Node: {node_id}')
                else:
                    async def get_targets_and_values_for_node(node: Node, targets = [], values = [], payload=payload):
                        fields = await get_children_fast(node)
                        field_names: list[str] = [name_to_mqtt((await get_display_name_fast(f)).Text) for f in fields]
                            
                        for i, field in enumerate(fields):
                            field_name = field_names[i]
                            if (field_name in payload.keys()) and (payload[field_name] is not None):
                                logging.debug(f'[MQTT->OPCUA] Found payload key for {field_name}, sending to node.')
                                datatype = (await get_datatype_as_str(field))
                                if datatype == 'Nested':
                                    logging.debug(f'[MQTT->OPCUA] Field {field.nodeid.to_string()} is nested, recursing...')
                                    await get_targets_and_values_for_node(field, targets, values, payload[field_name]) # recurse
                                elif datatype == 'Array':
                                    logging.debug(f'[MQTT->OPCUA] value {payload[field_name]} is Array, listing children...')
                                    array_nodes = (await get_children_fast(field))
                                    for (i, e) in enumerate(payload[field_name] or []):
                                        targets.append(array_nodes[i])
                                        values.append(e)
                                else:
                                    ua_value = value_to_ua(payload[field_name], datatype)
                                    targets.append(field)
                                    values.append(ua_value)
                        
                        return targets, values
                    
                    nodes_to_send, values = await get_targets_and_values_for_node(node)
                    nodes_to_send_display_names = [(await get_display_name_fast(n)).Text for n in nodes_to_send]
                    values_concise = [v.Value.Value for v in values]
                    logging.info(f'[MQTT->OPCUA] Sending to values for node {node}...')
                    await opcua_client.write_values(nodes_to_send, values)
                    logging.info(f'[MQTT->OPCUA] Sent values {values_concise} to Node {node_id} with fields {nodes_to_send_display_names}')
                
                    send_response(topic=topic, message=f'Sent values {values_concise} to Node {node_id} with fields {nodes_to_send_display_names}')
            except Exception as e:
                logging.error(f'[MQTT->OPCUA] Could not process payload {payload} on topic {topic} for leaf node {node_id}: {e} ({type(e)})')
                send_response(topic=topic, error=f'Failed to process payload {payload} for Node {node_id}: {e} ({type(e)})')
                
        mqtt_client.subscribe(topic, callback=send_to_opcua)
    await asyncio.Future()


async def listen_for_read_requests():
    """This function listens to a special topic called 'read', which accepts a list of topics. This function will then try to re-publish the stored state for those topics, if it exists. 
    """    
    topic = 'relay/read'
    mqtt_client = MqttClient()
    
    def try_push(payload):
        try:
            for requested_topic in payload['topics']:
                requested_topic = requested_topic.lstrip('relay')
                print(f'Read request for state on topic {requested_topic}')
                push_mqtt(requested_topic)
        except Exception as e:
            logging.error(f'Error parsing payload {payload} to read topics: {e}.')
            pass
    
    mqtt_client.subscribe(topic=topic, callback=try_push)
        
    await asyncio.Future()

async def main():    
    # OPC UA Client
    await add_opcua_client()
    
    # MQTT Client
    client = MqttClient()
    await client.connect()

    # Tasks
    await asyncio.gather(
        relay_opcua_to_mqtt(opcua_clients),
        relay_mqtt_to_opcua(opcua_clients[0]),
        listen_for_read_requests()
    )

if __name__ == "__main__":
    asyncio.run(main())
