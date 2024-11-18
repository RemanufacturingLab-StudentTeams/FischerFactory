import paho.mqtt.client as paho_client
import os
from logger import setup, c
import logging
from datetime import datetime
import re
from copy import deepcopy
import asyncio
from typing import List, Dict, Coroutine
from .page_topics import *
import json
from common import singleton_decorator as s

# Function to parse the MQTT schema and build the state variable from the specified topics for one page
def parse_mqtt_schema(topics: List[str] = []) -> Dict:
    path = f"{os.getenv('PROJECT_ROOT_PATH')}/schemas/mqtt/mqtt_schema.ts"
    
    res = {}
    
    # Define a function to generate default values
    def generate_default_payload(payload_str: str):
        defaults = {}
        # Split the payload into lines for processing
        for line in payload_str.strip().split(','):
            key_value = line.split(':')
            if len(key_value) == 2:
                key = key_value[0].strip()
                defaults[key] = None
        return defaults
    
    with open(path, 'r') as file:
        schema = file.read()
        schema = re.sub(r'//.*', '', schema) # remove all the comments
        
        for topic in topics:
            pattern = re.compile(
                # Regex pattern to match on the specified topic
                fr'\s*(\w+):\s*{{\s*topic:\s*[\'"](({topic})[^\'"]+)[\'"],?\s*payload:[^\}}]*}},?',
                re.DOTALL
            )
            
            matches = pattern.findall(schema)
            for match in matches:
                topic_name = match[1]
                payload_str = match[2]
                default_payload = generate_default_payload(payload_str)
                res[topic_name] = default_payload
            
            if len(matches) == 0:
                logging.warning(f"Topic {c(topic, 'white', 'cyan')} was specified in the page_topics file, but does not appear in the MQTT schema. This topic will not be subscribed to.")
    return res

@s.singleton
class MqttClient:
    """Wrapper class for an asynchronous MQTT client, provided with paho. Provides reconnection logic, connection status getters, and async pub/sub. Is a singleton.

    Raises:
        ConnectionRefusedError: If the MQTT broker is not reachable. In dev mode, make sure a broker (like `mosquitto`) is running on localhost:1883.

    Returns:
        MqttClient: A new instance if none exists, or the existing instance.
    """    
    state_data = {'dirty': False} # dirty bit to track if it was modified since it was last GET-ed
    state_overview = {'dirty': False}
    connection_status = False
    
    def __init__(self) -> None:
        if not hasattr(self, 'initialized'):  # Prevent reinitialization
            self.broker_ip = os.getenv('MQTT_BROKER_IP')
            self.broker_port = int(os.getenv('MQTT_BROKER_PORT', 1883))
            self.client_id = os.getenv('MQTT_CLIENT_ID', 'mqtt_client')
            
            # MQTT Client setup
            self.client = paho_client.Client(client_id=self.client_id)
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.on_disconnect = self.on_disconnect
            self.client.on_publish = self.on_publish
            self.client.on_subscribe = self.on_subscribe
            
            self.client.username_pw_set(
                username=os.getenv('MQTT_USERNAME'),
                password=os.getenv('MQTT_PASSWORD')
            )
            
            self.initialized = True 
            self.reconnect_attempts = 0
            self.max_reconnect_attempts = 10
            self.reconnect_interval = 5
            
            asyncio.create_task(self.connect())

    async def connect(self):
        try:
            logging.info(f"[MQTTCLIENT] Connecting to MQTT broker at {self.broker_ip}:{self.broker_port}")
            await asyncio.to_thread(self.client.connect, self.broker_ip, self.broker_port)
            await asyncio.to_thread(self.client.loop_start)
            self.connection_status = True
            self.reconnect_attempts = 0
            
            await self.init_state_variables()
        except Exception as e:
            logging.error(f"[MQTTCLIENT] Failed to connect to MQTT broker: {e}")
            self.connection_status = False
            self.reconnect_attempts += 1
            if self.reconnect_attempts <= self.max_reconnect_attempts:
                logging.info(f"[MQTTCLIENT] Attempting reconnection attempt {self.reconnect_attempts}/{self.max_reconnect_attempts}")
                await asyncio.create_task(self.attempt_reconnection())
            else:
                logging.error("[MQTTCLIENT] Max reconnection attempts reached. Stopping MQTT client.")
                raise ConnectionRefusedError()

    async def attempt_reconnection(self):
        await asyncio.sleep(self.reconnect_interval)
        await self.connect()

    def disconnect(self):
        logging.info("[MQTTCLIENT] Disconnected from MQTT broker")
        self.connection_status = False

    async def publish(self, topic, payload, qos=1):
        try:
            result = self.client.publish(topic, payload, qos=qos)
            result.wait_for_publish()
            logging.info(f"[MQTTCLIENT] Published message to topic {c(topic, 'white', 'cyan')}: {c(payload, 'white', 'cyan')} (Result: {result.rc})")
        except Exception as e:
            logging.error(f"[MQTTCLIENT] Publish to topic {c(topic, 'white', 'cyan')} failed: {e}")

    async def subscribe(self, topic: str, qos=1, callback=None):
        logging.info(f"[MQTTCLIENT] Subscribing to topic {c(topic, 'white')}")
        
        @self.client.topic_callback(topic)
        def on_message_wrapper(client, userdata, msg):
            payload = msg.payload.decode()
            logging.debug(f"[MQTTCLIENT] Received message on topic {c(topic, 'cyan', 'white')}: {c(payload, 'cyan')}")
            if callback:
                callback(payload)  

        self.client.message_callback_add(topic, on_message_wrapper)
        self.client.subscribe(topic, qos=qos)
        
    async def unsubscribe(self, topic: str):
        self.client.unsubscribe(topic)

    # Callback functions
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info("[MQTTCLIENT] Connected to MQTT broker")
        else:
            logging.error(f"Failed to connect, return code {rc}")

    def on_message(self, client, userdata, msg):
        logging.info(f"[MQTTCLIENT] Message received from {c(msg.topic, 'white', 'cyan')}: {msg.payload.decode()}")

    def on_disconnect(self, client, userdata, rc):
        logging.info("[MQTTCLIENT] Disconnected from MQTT broker")
        self.connection_status = False

    def on_publish(self, client, userdata, mid):
        logging.info(f"[MQTTCLIENT] Message {mid} published successfully")

    def on_subscribe(self, client, userdata, mid, granted_qos):
        logging.info(f"[MQTTCLIENT] Subscribed to topic, mid: {mid}, qos: {granted_qos}")
        
    # calls parse_mqtt_schema for each page to make a state variable for each of them
    async def init_state_variables(self) -> None: 
        # state variable for the "overview" page
        self.state_overview.update(parse_mqtt_schema(OVERVIEW_TOPICS)) # raw topics as specified by the page_topics.py file
        await self.subscribe_to_state(self.state_overview)
        self.state_data.update(parse_mqtt_schema(DATA_TOPICS))
        await self.subscribe_to_state(self.state_data)
        
    async def subscribe_to_state(self, state): # subscribes to f/i/ topics and updates the state_in global variable.
        subscription_tasks = []
        for key in state:
            if key == 'dirty': continue
            def cb(message, key=key): # callback to make sure the mqtt messages get stored in the state variable
                p = json.loads(message)
                for k in p:
                    v = p[k]
                    if (v is not None) and (v != '\"\"') and (v != ''): # if the value exists in the JSON and isn't an empty string
                        state[key][k] = v
                state['dirty'] = True
            subscription_tasks.append(self.subscribe(topic=key, callback=cb))
        
        await asyncio.gather(*subscription_tasks)
        
    def get_state(self, page):
        match page:
            case 'overview':
                res = deepcopy(self.state_overview)
                self.state_overview['dirty'] = False
                return res
            case 'data':
                res = deepcopy(self.state_data)
                self.state_data['dirty'] = False
                return res
            
    def get_status(self) -> bool:
        return self.connection_status
    
    def get_reconnection_attempts(self) -> int:
        return self.reconnect_attempts