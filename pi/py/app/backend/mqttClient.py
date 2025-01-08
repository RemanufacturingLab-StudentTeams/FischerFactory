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
from typing import Callable, Optional
from common import RuntimeManager

@s.singleton
class MqttClient:
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
            self.reconnect_attempts = 0
        except Exception as e:
            logging.error(f"[MQTTCLIENT] Failed to connect to MQTT broker: {e}")
            self.connection_status = False
            self.reconnect_attempts += 1
            if self.reconnect_attempts <= self.max_reconnect_attempts:
                logging.warning(f"[MQTTCLIENT] Attempting reconnection attempt {self.reconnect_attempts}/{self.max_reconnect_attempts}")
                await asyncio.create_task(self.attempt_reconnection())
            else:
                logging.error("[MQTTCLIENT] Max reconnection attempts reached. Stopping MQTT client.")
                raise ConnectionRefusedError()

    async def attempt_reconnection(self):
        await asyncio.sleep(self.reconnect_interval)
        await self.connect()

    def disconnect(self):
        logging.info("[MQTTCLIENT] Disconnected from MQTT broker")

    async def publish(self, topic, payload, qos=1):
        # convert payload to JSON
        payload = json.dumps(payload)
        
        result = self.client.publish(topic, payload, qos=qos)
        logging.info(f"[MQTTCLIENT] Published message to topic {c(topic, 'white', 'cyan')}: {c(payload, 'white', 'cyan')} (Result: {result.rc})")

    async def subscribe(self, topic, qos=1, callback: Optional[Callable] = None):
        logging.info(f"[MQTTCLIENT] Subscribing to topic {c(topic, 'white')}")
        
        @self.client.topic_callback(topic)
        def on_message_wrapper(client, userdata, msg):
            payload = msg.payload.decode()
            res = ''
            try:
                res = json.loads(payload)
            except Exception as e:
                logging.error(f"[MQTTCLIENT] Payload is not valid JSON: {payload}")
                logging.debug(f"[MQTTCLIENT] Received message on topic {c(topic, 'white', 'cyan')}: {c(res, 'white')}")
            
            if asyncio.iscoroutinefunction(callback):
                rtm = RuntimeManager()
                rtm.add_task(callback(res))
            elif callback:
                callback(res)

        self.client.message_callback_add(topic, on_message_wrapper)
        self.client.subscribe(topic, qos=qos)

    # Callback functions
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connection_status = True
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
            
    def get_status(self) -> bool:
        return self.connection_status
    
    def get_reconnection_attempts(self) -> int:
        return self.reconnect_attempts