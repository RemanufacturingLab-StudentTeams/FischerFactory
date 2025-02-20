from asyncua import Node
from asyncua.common.subscription import DataChangeNotificationHandlerAsync, DataChangeNotif
from paho.mqtt.client import Client as MqttClient
from helper import get_display_name_fast, name_to_mqtt, value_to_mqtt, get_datatype_as_str
from state import push_mqtt, state
import asyncio
import json
from typing import Optional, Any
from asyncua.ua import Variant
import logging
from datetime import date, datetime
    
def _parse_value(value: Any, EXCLUDE=None) -> Any:
    if not isinstance(value, (date, datetime, int, str, bool, float)):
        if isinstance(value, list):
            return [_parse_value(v) for v in value if (hasattr(v, '__dict__') and v.__dict__.get('i_code') != 0)]
        return {
            name_to_mqtt(k): _parse_value(v) 
            for k, v in value.__dict__.items() if k != EXCLUDE
        }
    else:
        return value

class LeafDataChangeHandler(DataChangeNotificationHandlerAsync):
    def __init__(self, mqtt_client: MqttClient, topic: str, EXCLUDE:Optional[list[str]]=None):
        self.mqtt_client = mqtt_client
        self.topic = '/'+topic
        topic_parts = topic.split('/')
        partial_state = state
        for topic_part in topic_parts:
            topic_part = '/' + topic_part
            if partial_state.get(topic_part) is None:
                partial_state[topic_part] = {}
            partial_state = partial_state[topic_part]
        self.partial_state = partial_state # Maintain a reference to the overall state
        self.EXCLUDE = EXCLUDE
    
    async def datachange_notification(self, node: Node, value, data: DataChangeNotif) -> None:
        try:
            v: Variant = data.monitored_item.Value.Value
            if v.VariantType.name != 'ExtensionObject':
                logging.warning(f'[OPCUA->MQTT] Variant for node {(await node.read_display_name()).Text} was expected to be an ExtensionObject, but was: {v.VariantType.name}.')
            
            parsed = _parse_value(v.Value, self.EXCLUDE)
            self.partial_state.update(parsed)
            push_mqtt(self.topic)
                
        except Exception as e:
            logging.error(f'[OPCUA->MQTT] Failed to process payload for node {node}: {e}')
        
class FieldDataChangeHandler(DataChangeNotificationHandlerAsync):
    def __init__(self, mqtt_client: MqttClient, topic: str):
        self.mqtt_client = mqtt_client
        self.queue = asyncio.Queue()
        self.topic = '/'+topic
        topic_parts = topic.split('/')
        partial_state = state
        for topic_part in topic_parts:
            topic_part = '/' + topic_part
            if partial_state.get(topic_part) is None:
                partial_state[topic_part] = {}
            partial_state = partial_state[topic_part]
        self.partial_state = partial_state # Maintain a reference to the overall state

    async def datachange_notification(self, node: Node, value, data: DataChangeNotif) -> None:
        try:        
            v: Variant = data.monitored_item.Value.Value
            parsed = _parse_value(v.Value)
            name = name_to_mqtt((await get_display_name_fast(node)).Text)
            self.partial_state[name] = parsed
            push_mqtt(self.topic)
                
        except Exception as e:
            logging.error(f'[OPCUA->MQTT] Failed to process payload for idependent field node {node}: {e}')
        
    def status_change_notification(self, status):
        print(f"Status change notification: {status}")