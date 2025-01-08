import asyncio
from asyncio import run_coroutine_threadsafe
import json
from asyncua import Node, ua
from asyncua import Client as OPCUAClient
from paho.mqtt import client as mqtt_client
from paho.mqtt.client import Client as MqttClient
from dotenv import load_dotenv
import os
from mappings import mappings, special_rules
from datetime import datetime
from helper import name_to_mqtt, value_to_ua, get_datatype_as_str
from opcua_datachange_handler import LeafDataChangeHandler, FieldDataChangeHandler

# Load environment variables
load_dotenv()
PLC_IP = os.getenv('PLC_IP')
PLC_PORT = int(os.getenv('PLC_PORT'))
MQTT_BROKER_IP = os.getenv('MQTT_BROKER_IP')
MQTT_BROKER_PORT = int(os.getenv('MQTT_BROKER_PORT'))
MQTT_USERNAME = os.getenv('MQTT_USERNAME')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')

async def relay_opcua_to_mqtt(opcua_client: OPCUAClient, mqtt_client: mqtt_client.Client):
    async def subscribe_recursive(node: Node, base_topic: str):
        node_name = (await node.read_display_name()).Text
        print(f"[MQTT_RELAY] Recursively subscribing to '{node_name}', mapping to topic '{base_topic}'")
        children = await node.get_children()
        has_grandchildren = len(await children[0].get_children()) != 0
        if not has_grandchildren:  # Leaf node, children is payload
            print(f'Node {node_name} is leaf')
            if (await node.read_node_class()) == 2: 
                handler = LeafDataChangeHandler(mqtt_client, base_topic)
                subscription = await opcua_client.create_subscription(period=1000, handler=handler)
                await handler.read_initial_value(node=node)
                await subscription.subscribe_data_change(node)
            else: # Sometimes a leaf node is not a UAVariable type, which means it cannot be subscribed to. In this case, subscribe to the fields individually 
                for field in (await node.get_children()):
                    handler = FieldDataChangeHandler(mqtt_client, base_topic)
                    subscription = await opcua_client.create_subscription(period=1000, handler=handler)
                    await handler.read_initial_value(node=field)
                    await subscription.subscribe_data_change(field)
        else:  # Non-leaf node (i.e., it has grandchildren), recurse
            for child in children:
                child_name = (await child.read_display_name()).Text
                print(f'Found child {child_name}')
                if not child_name:
                    raise ValueError(f'Child {child} has no display name.')
                mqtt_sub_topic = f"{base_topic}/{name_to_mqtt(child_name)}"
                print(f'Generated subtopic: {mqtt_sub_topic} from {child_name}')
                await subscribe_recursive(child, mqtt_sub_topic)

    async with opcua_client:
        for mapping in mappings:
            print(f'[MQTT_RELAY] Mapping {mapping.FROM} to {mapping.TO}')
            if mapping.FROM.startswith('"'):  # OPC UA -> MQTT
                root_node: Node = opcua_client.get_node('ns=3;s=' + mapping.FROM)
                base_topic = mapping.TO
                await subscribe_recursive(root_node, base_topic)

async def relay_mqtt_to_opcua(opcua_client: OPCUAClient, mqtt_client: MqttClient):
    async def handle_message(opcua_client: OPCUAClient, topic, payload):
        for mapping in mappings:
            if mapping.FROM == topic:
                node_id = 'ns=3;s=' + mapping.TO
                payload_dict = json.loads(payload)
                if not isinstance(payload_dict, dict):
                    raise ValueError(f'Payload of topic {topic} was expected to be a dict, but it was {payload_dict}')
                node = opcua_client.get_node(node_id)
                fields = await node.get_children()
                nodes = []
                values = []
                for field in fields:
                    payload_key = name_to_mqtt(await field.read_display_name())
                    if payload_key in payload_dict.keys():
                        nodes.append(field)
                        values.append(value_to_ua(payload_dict[payload_key], get_datatype_as_str(field)))
                
                await opcua_client.write_values(nodes, values)

    def on_message(client, userdata, msg):
        loop = asyncio.get_event_loop()
        run_coroutine_threadsafe(
            handle_message(opcua_client, msg.topic, msg.payload),
            loop
        )
                
    async with opcua_client:
        mqtt_client.on_message = on_message
        mqtt_client.subscribe([
            (mapping.FROM, 0) for mapping in mappings if not mapping.FROM.startswith('"')
        ])

async def main():
    # OPC UA Client
    opcua_client = OPCUAClient(f"opc.tcp://{PLC_IP}:{PLC_PORT}")
    async def connect_opuca():
        try:
            await opcua_client.connect()
            print(f'Connected to PLC OPCUA server at <{PLC_IP}:{PLC_PORT}>')
        except Exception as e:
            print(f'Failed to connect to PLC at <{PLC_IP}:{PLC_PORT}>: {e}')
            print('Retrying a second...')
            await asyncio.sleep(1)
            await connect_opuca()

    await connect_opuca()

    client = MqttClient()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    async def connect_mqtt() -> MqttClient:
        try:
            client.connect(MQTT_BROKER_IP, MQTT_BROKER_PORT)
            print(f'Connected to MQTT broker at <{MQTT_BROKER_IP}:{MQTT_BROKER_PORT}>')
            return client
        except Exception as e:
            print(f'Failed to connect to MQTT broker at <{MQTT_BROKER_IP}:{MQTT_BROKER_PORT}>: {e}')
            await asyncio.sleep(1)
            return await connect_mqtt()
    
    # MQTT Client
    mqtt_client = await connect_mqtt()
    mqtt_client.loop_start()

    # Tasks
    await asyncio.gather(
        relay_opcua_to_mqtt(opcua_client, mqtt_client)
        # relay_mqtt_to_opcua(opcua_client, mqtt_client),
    )

if __name__ == "__main__":
    asyncio.run(main())
