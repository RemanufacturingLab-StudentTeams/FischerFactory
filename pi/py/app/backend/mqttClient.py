import paho.mqtt.client as paho_client
import os
from logger import setup
import logging
from datetime import datetime
import re 
import json
import asyncio

setup()

# Helper functions

# Function to parse the MQTT schema and build the state_in variable from that
def parse_mqtt_schema():
    path = f"{os.getenv('PROJECT_ROOT_PATH')}/schemas/mqtt/mqtt_schema.ts"
    
    res = {}
    
    # Define a regex pattern to match the topic and payload
    pattern = re.compile(
        r'\s*(\w+):\s*{\s*topic:\s*[\'"]((f/i/)[^\'"]+)[\'"],\s*payload:\s*{([^}]*)}\s*},?',
        re.DOTALL
    )
    
    # Define a function to generate default values
    def generate_default_payload(payload_str):
        defaults = {}
        # Split the payload into lines for processing
        for line in payload_str.strip().split(','):
            key_value = line.split(':')
            if len(key_value) == 2:
                key = key_value[0].strip()
                value_type = key_value[1].strip()
                # Assign default values based on type
                if 'number' in value_type:
                    defaults[key] = 0
                elif 'string' in value_type:
                    defaults[key] = ""
                elif 'Date' in value_type:
                    defaults[key] = datetime.now().isoformat()  # Using ISO format for date
                else:
                    defaults[key] = None  # Default for unspecified types
        return defaults

    with open(path, 'r') as file:
        content = file.read()
        
        # Find all matches in the content
        for match in pattern.finditer(content):
            # Extract topic and payload
            topic_name = match.group(2)
            payload_str = match.group(3)
            default_payload = generate_default_payload(payload_str)
            res[topic_name] = default_payload
    return res

class MqttClient:
    
    _instance = None
    def __new__(cls, *args, **kwargs): # singleton pattern
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.client = None
        return cls._instance
    
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
            
            global state_in
            state_in = parse_mqtt_schema()
            
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
            self.reconnect_attempts = 0
            
            await self.subscribe_to_state_in()
        except Exception as e:
            logging.error(f"Failed to connect to MQTT broker: {e}")
            self.reconnect_attempts += 1
            if self.reconnect_attempts <= self.max_reconnect_attempts:
                logging.info(f"Attempting reconnection attempt {self.reconnect_attempts}/{self.max_reconnect_attempts}")
                await asyncio.create_task(self.attempt_reconnection())
            else:
                logging.error("Max reconnection attempts reached. Stopping MQTT client.")
                
    async def subscribe_to_state_in(self): # subscribes to f/i/ topics and updates the state_in global variable.
        subscription_tasks = []
        for key in state_in:
            def cb(message, key=key):
                state_in[key] = message
                print(json.dumps(state_in, indent=4))
            
            subscription_tasks.append(self.subscribe(topic=key, callback=cb))
        
        await asyncio.gather(*subscription_tasks)

    async def attempt_reconnection(self):
        await asyncio.sleep(self.reconnect_interval)
        await self.connect()

    def disconnect(self):
        logging.info("[MQTTCLIENT] Disconnected from MQTT broker")

    async def publish(self, topic, payload, qos=1):
        result = self.client.publish(topic, payload, qos=qos)
        logging.info(f"[MQTTCLIENT] Published message to topic {topic}: {payload} (Result: {result.rc})")

    async def subscribe(self, topic, qos=1, callback=None):
        logging.info(f"[MQTTCLIENT] Subscribing to topic {topic}")
        def on_message_wrapper(client, userdata, msg):
            payload = msg.payload.decode()
            if callback:
                callback(payload)  

        self.client.message_callback_add(topic, on_message_wrapper)
        self.client.subscribe(topic, qos=qos)

    # Callback functions
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info("[MQTTCLIENT] Connected to MQTT broker")
        else:
            logging.error(f"Failed to connect, return code {rc}")

    def on_message(self, client, userdata, msg):
        logging.info(f"[MQTTCLIENT] Message received from {msg.topic}: {msg.payload.decode()}")

    def on_disconnect(self, client, userdata, rc):
        logging.info("[MQTTCLIENT] Disconnected from MQTT broker")

    def on_publish(self, client, userdata, mid):
        logging.info(f"[MQTTCLIENT] Message {mid} published successfully")

    def on_subscribe(self, client, userdata, mid, granted_qos):
        logging.info(f"[MQTTCLIENT] Subscribed to topic, mid: {mid}, qos: {granted_qos}")