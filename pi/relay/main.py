import asyncio
import json
from asyncua import Client, Node, ua
from paho.mqtt import client as mqtt_client
from dotenv import load_dotenv
import os
from mappings import mappings, special_rules
from datetime import datetime
from helper import convert, convert_to_mqtt_format, convert_to_opcua_format, _convert_to_correct_type, _get_data_type_from_node_id

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
        if not children:  # Leaf node
            async def on_data_change(node: Node, val, _):
                
                if isinstance(val, dict):
                    # Convert field names to MQTT format and retain structure
                    mqtt_payload = {
                        convert_to_mqtt_format(k): _convert_to_correct_type(v, _get_data_type_from_node_id(node.nodeid))
                        for k, v in val.items()
                    }
                else:
                    raise ValueError('OPCUA Node payloads should always be a dict.')
                mqtt_client.publish(base_topic, json.dumps(mqtt_payload))

            await node.subscribe_data_change(on_data_change)
        else:  # Non-leaf node, recurse
            for child in children:
                child_name = await child.read_browse_name()
                mqtt_sub_topic = f"{base_topic}/{convert_to_mqtt_format(child_name.Name)}"
                await subscribe_recursive(child, mqtt_sub_topic)

    async with opcua_client:
        for mapping in mappings:
            if mapping.FROM.startswith('"'):  # OPC UA -> MQTT
                root_node: Node = opcua_client.get_node(mapping.FROM)
                base_topic = mapping.TO
                await subscribe_recursive(root_node, base_topic)

async def relay_mqtt_to_opcua(opcua_client: Client, mqtt_client: mqtt_client.Client):
    async with opcua_client:
        def on_message(client, userdata, msg):
            for mapping in mappings:
                if mapping.FROM == msg.topic:
                    node: Node = opcua_client.get_node(mapping.TO)
                    payload = json.loads(msg.payload)
                    value = payload.get("value")
                    if value is not None:
                        node.write_value(value)

        mqtt_client.on_message = on_message
        mqtt_client.subscribe([(mapping.FROM, 0) for mapping in mappings if not mapping.FROM.startswith('"')])

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
