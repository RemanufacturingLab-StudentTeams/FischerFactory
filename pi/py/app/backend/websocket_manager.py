from common import singleton, RuntimeManager
import os 
import logging 
from backend import MqttClient
from websockets.server import ServerConnection
from websockets.http11 import Request
import websockets
from datetime import date, datetime
import asyncio
import json 
    
@singleton
class WebSocketManager:
    def __init__(self):
        self.connections: dict[str, ServerConnection] = {} 

    async def connection_handler(self, conn: ServerConnection):
        """Handles WebSocket connections and messages."""
        try:
            async for message in conn:
                logging.debug(f"[WS_SERVER] Received: {message}")
        except websockets.ConnectionClosed:
            logging.debug(f'[WS_SERVER] Client disconnected')
            topic = [k for k, v in self.connections if v == conn][0]
            mqttClient = MqttClient()
            mqttClient.client.unsubscribe(topic)
            self.connections.pop(topic)
    
    def request_handler(self, conn: ServerConnection, req: Request):
        topic = req.path.lstrip('/')
        logging.debug(f'[WS_SERVER] Adding ServerConnection for {topic}')
        self.connections[topic] = conn
        
        rtm = RuntimeManager()
        mqttClient = MqttClient()
        
        if topic.startswith('f/'):
            # hydrate
            rtm.add_task( 
                mqttClient.publish(
                    "read",
                    {
                        "topics": [topic]
                    }
                )
            )
        
        async def cb(msg: dict, conn=conn, topic=topic):
            logging.debug(f'[WS_SERVER] Received message on {topic}')
            if msg.get('ts'): # Filter out midnight times, which the PLC ues as a default when it has no time data sometimes
                t = None
                try:
                    t = datetime.strptime(msg['ts'], '%Y-%m-%dT%H:%M:%S.%f%z').time()
                except Exception:
                    t = datetime.strptime(msg['ts'], '%Y-%m-%dT%H:%M:%S%z').time()
                if (t.hour == 0) and (t.minute == 0) and (t.second == 0):
                    msg['ts'] = ''
            try:
                await conn.send(json.dumps(msg))
                logging.debug(f'[WS_SERVER] Data from {topic} sent to frontend.')
            except websockets.ConnectionClosed:
                MqttClient().client.unsubscribe(topic)
                self.connections.pop(topic)
            except Exception as e:
                logging.error(f"[WS_SERVER] Failed to send message to frontend WebSocket {topic}: {e} ({type(e)})")
        rtm.add_task(
            mqttClient.subscribe(
                topic,
                callback=cb
            )
        )
    
    async def run_server(self):
        logging.info(f"Starting WebSocket server on ws://localhost:{os.getenv('WS_PORT')}...")
        async with websockets.serve(
            handler=self.connection_handler, 
            host="localhost", 
            port=8765, 
            process_request=self.request_handler
        ):
            logging.info("WebSocket server is running.")
            await asyncio.Future()