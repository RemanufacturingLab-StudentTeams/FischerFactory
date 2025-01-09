from asyncua import Node
from asyncua.common.subscription import DataChangeNotificationHandler, DataChangeNotif
from paho.mqtt.client import Client as MqttClient
from helper import name_to_mqtt, value_to_mqtt, get_datatype_as_str
from state import push_mqtt, state
import asyncio
import json
from typing import Optional

async def _read_value_nested(node: Node): # Reads the value of a potentially nested node to a potentially nested Python object
    dt = await get_datatype_as_str(node)
    if dt == 'Nested':
        res = {}
        for child in (await node.get_children()):
            child_name = (await child.read_display_name()).Text
            res[name_to_mqtt(child_name)] = await _read_value_nested(child)
        return res
    else:
        return value_to_mqtt(await node.read_value(), dt)

class LeafDataChangeHandler(DataChangeNotificationHandler):
    def __init__(self, mqtt_client: MqttClient, topic: str, EXCLUDE:Optional[list[str]]=None):
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
        self.EXCLUDE = EXCLUDE
        
    async def read_initial_value(self, node: Node):
        for child in (await node.get_children()):
            name = (await child.read_display_name()).Text
            if self.EXCLUDE:
                if name in self.EXCLUDE:
                    print(f'Skipping explicitly excluded field {name}')
                    continue
            name = name_to_mqtt(name)
            print(f'Added to partial state {name}: {(await get_datatype_as_str(child))}')
            self.partial_state[name] = await _read_value_nested(child)
        print(self.partial_state)
        push_mqtt(self.topic, self.mqtt_client)
    
    def datachange_notification(self, node: Node, value, data: DataChangeNotif) -> None:
        self.queue.put_nowait([node, value, data])
    
    async def process(self): # on_data_change will be applied to each child
        try:
            while True:
                [node, value, data] = self.queue.get_nowait()
                
                children: list[Node] = await node.get_children()
            
                # Convert field names to MQTT format and retain structure
                for child in children:
                    name = (await child.read_display_name()).Text
                    if not name:
                        raise ValueError(f'Child {child} has no display name.')
                    if self.EXCLUDE:
                        if name in self.EXCLUDE:
                            print(f'Skipping explicitly excluded field {name}')
                            continue
                    name = name_to_mqtt(name)
                    self.partial_state[(name_to_mqtt(name=name))] = await _read_value_nested(child)
                push_mqtt(self.topic, self.mqtt_client)
                
        except asyncio.QueueEmpty:
            pass
        
class FieldDataChangeHandler(DataChangeNotificationHandler):
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
        
    async def read_initial_value(self, node: Node):
        name = name_to_mqtt((await node.read_display_name()).Text)
        print(f'Added to partial state {name}: {(await get_datatype_as_str(node))}')
        self.partial_state[name] = await _read_value_nested(node)
        push_mqtt(self.topic, self.mqtt_client)
    
    def datachange_notification(self, node: Node, value, data: DataChangeNotif) -> None:
        self.queue.put_nowait([node, value, data])
    
    async def process(self): # on_data_change will be applied to each child
        try:
            while True:
                [node, value, data] = self.queue.get_nowait()
            
                # Convert field names to MQTT format and retain structure
                name = name_to_mqtt((await node.read_display_name()).Text)
                value = await node.read_value()
                
                self.partial_state[name] = await _read_value_nested(node)
                push_mqtt(self.topic, self.mqtt_client)
                
        except asyncio.QueueEmpty:
            pass