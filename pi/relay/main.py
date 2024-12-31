import asyncio
from asyncio import run_coroutine_threadsafe
import json
from asyncua import Client, Node, ua
from paho.mqtt import client as mqtt_client
from dotenv import load_dotenv
import os
from mappings import mappings, special_rules
from datetime import datetime
from helper import name_to_mqtt, value_to_mqtt, value_to_ua, get_data_type_from_node_id

# Load environment variables
load_dotenv()
PLC_IP = os.getenv('PLC_IP')
PLC_PORT = int(os.getenv('PLC_PORT'))
MQTT_BROKER_IP = os.getenv('MQTT_BROKER_IP')
MQTT_BROKER_PORT = int(os.getenv('MQTT_BROKER_PORT'))
MQTT_USERNAME = os.getenv('MQTT_USERNAME')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')

async def relay_opcua_to_mqtt(opcua_client: Client, mqtt_client: mqtt_client.Client):
    async def subscribe_recursive(node: Node, base_topic: str):
        children = await node.get_children()
        has_grandchildren = len(await children[0].get_children()) is not 0
        if not has_grandchildren:  # Leaf node, children is payload
            async def on_data_change(node: Node, val, _): # on_data_change will be applied to each child
                
                mqtt_payload = {}
                
                # Convert field names to MQTT format and retain structure
                for child in children:
                    name = (await child.read_display_name()).Text
                    if not child_name:
                        raise ValueError(f'Child {child} has no display name.')
                    value = await child.get_value()
                    
                    mqtt_payload.update({name_to_mqtt(name): value_to_mqtt(value)})
                
                mqtt_client.publish(base_topic, json.dumps(mqtt_payload))

            await node.subscribe_data_change(on_data_change)
        else:  # Non-leaf node (i.e., it has grandchildren), recurse
            for child in children:
                child_name = (await child.read_display_name()).Text
                if not child_name:
                    raise ValueError(f'Child {child} has no display name.')
                mqtt_sub_topic = f"{base_topic}/{name_to_mqtt(child_name)}"
                await subscribe_recursive(child, mqtt_sub_topic)

    async with opcua_client:
        for mapping in mappings:
            if mapping.FROM.startswith('"'):  # OPC UA -> MQTT
                root_node: Node = opcua_client.get_node('ns=3;s=' + mapping.FROM)
                base_topic = mapping.TO
                await subscribe_recursive(root_node, base_topic)

async def relay_mqtt_to_opcua(opcua_client: Client, mqtt_client: mqtt_client.Client):
    async def handle_message(opcua_client: Client, topic, payload):
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
                        values.append(value_to_ua(payload_dict[payload_key], get_data_type_from_node_id(field.nodeid)))
                
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

def connect_mqtt():
    client = mqtt_client.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.connect(MQTT_BROKER_IP, MQTT_BROKER_PORT)
    return client

async def main():
    # OPC UA Client
    opcua_client = Client(f"opc.tcp://{PLC_IP}:{PLC_PORT}")

    # MQTT Client
    mqtt_client = connect_mqtt()
    mqtt_client.loop_start()

    # Tasks
    await asyncio.gather(
        relay_opcua_to_mqtt(opcua_client, mqtt_client),
        relay_mqtt_to_opcua(opcua_client, mqtt_client),
    )

if __name__ == "__main__":
    asyncio.run(main())
