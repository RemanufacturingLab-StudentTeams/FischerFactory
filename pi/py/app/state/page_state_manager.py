from common import config
from common import singleton_decorator as s
from typing import Any
import asyncio
import logging
from asyncio import Task
from state import state_data_schema
from dash_extensions import WebSocket as FrontEndWebSocket
import websockets
from websockets.client import ClientConnection as BackEndWebSocket
import os
import json
from backend import mqttClient

@s.singleton
class PageStateManager:
    '''Manages and fetches state from external sources (MQTT or OPCUA). It is more or less a buffer, so that the results of async calls can be made accessible to Dash callbacks. It is a singleton.
    '''
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.mqttClient = mqttClient.MqttClient()
            self.monitor_tasks: list[Task[Any]] = []
            self.global_monitor_tasks: list[Task[Any]] = []
            self.data = state_data_schema._data
            self.ws_clients: dict[str, BackEndWebSocket] = {}
    
            self.initialized = True
    
    async def hydrate_page(self, page: str):
        """Meant to fetch data once (as opposed to monitoring, which fetches continually), used to fetch static (unchanging) data for a page. 
        It does this by sending a read request to the relay to re-publish all PLC values.
        For other MQTT data sources, it unfortunately cannot request data, because MQTT does not natively support read requests.
        
        Args:
            page (str): Which page to fetch hydration data for.
        """
        await self.mqttClient.publish(
            os.getenv('MQTT_RELAY_TOPIC')+'/read',
            {
                'topics': [
                    topic.lstrip('relay/') 
                    for topic 
                    in self.data.get(page, {}).values() 
                    if topic.startswith('relay') # only send read requests for PLC topics
                ]
            }
        )
    
    async def stop_monitoring(self):
        """Stop all monitoring tasks."""
        logging.debug(f'[PSM] Stopping all monitoring tasks')
        
        for task in self.monitor_tasks:
            try:
                task.cancel()
                await task  # Ensure the task is properly canceled
            except asyncio.CancelledError as e: # this is actually fine, it should give a CancelledError because it was cancelled
                pass
        self.monitor_tasks = []

    async def monitor_page(self, page: str):
        """Called on page load. Stops all previous monitoring tasks and starts monitoring data for the requested page. 
        When it receives a message on a topic, it emits this value over a WebSocket using the page and key for the pathname. For instance, when monitoring the `factory-overview` page, it will emit on `factory-overview/plc_version` and `factory-overview/turtlebot_current_state`.
        On the clientside, a clientside callback listens on this websocket and stores the value in a dcc.Store, so it can be accessed by the GUI.

        Args:
            page (str): Which page to poll/subscribe to monitoring data for.
        """
        
        is_global = page == 'global'
        
        # Cancel any existing monitoring tasks
        if not is_global:
            await self.stop_monitoring()
        
        logging.debug(f'[PSM] Monitoring page: {page} with data: {[k for k, s in self.data.get(page, {}).items()]}')

        # Create monitoring tasks for OPCUA and MQTT sources
        for key, topic in self.data.get(page, {}).items():
            async def callback(message, key=key): # Push MQTT data to frontend with websockets
                try:
                    logging.debug(f'[PSM] Received message: {json.dumps(message)}')
                    await self.ws_clients.get(key).send(json.dumps(message))
                    logging.debug(f'[PSM] Sent to FrontEnd WebSocket {key} via Backend WebSocket {self.ws_clients.get(key).id}')
                except Exception as e:
                    logging.error(f'[PSM] Failed to push external data to frontend with WebSocket: {e}.')
                    logging.debug(self.ws_clients)
            if is_global:
                self.global_monitor_tasks.append(asyncio.create_task(
                    self.mqttClient.subscribe(
                        topic, 
                        qos=1, 
                        callback=callback
                    )
                ))
            else: 
                self.monitor_tasks.append(asyncio.create_task(
                self.mqttClient.subscribe(
                    topic,
                    qos=1, 
                    callback=callback
                )
            ))

        if is_global:
            await asyncio.gather(*self.global_monitor_tasks)
        else:
            await asyncio.gather(*self.monitor_tasks)  # Await all tasks
    
    async def send_data(self, page: str, key: str, data: dict):
        """Publish a data item to a source.

        Args:
            page (str): Page to that contains the key. Use a hyphen as a delimiter. Example: `factory-data`.
            data (dict): A dictionary that will be translated to JSON to send to the broker. Example: {'order_do_oven': True, 'order_bake_time': 4000}.
        """
        if page not in self.data:
            return
        
        topic = self.data.get(page, {}).get(key, {})
        
        logging.debug(f'[PSM] Sending user data: {data} over {topic}')
        await self.mqttClient.publish(topic, data)
        
    async def generate_websockets(self, page: str) -> list[FrontEndWebSocket]:
        """Must be called in the layout variable of every page to receive external data updates. Generates the WebSocket components that function as endpoints for the PSM to send external data to.

        Args:
            page (str): Page to that contains the key. Use a hyphen as a delimiter. Example: `factory-data`.
        """
        
        res = []
        for (key, topic) in self.data.get(page, {}).items():
            url = f"ws://localhost:{os.getenv('WS_PORT')}/{key}"
            
            frontendWS = FrontEndWebSocket(id=f'mqtt:{key}', url=url, message=None)
            backendWS = await websockets.connect(url)
            logging.debug(f"[PSM] Generated frontend WebSocket: id=mqtt:{key} on url=ws://localhost:{os.getenv('WS_PORT')}/{key}")
            self.ws_clients[key] = backendWS # update registry so stuff can be sent to the clients
            logging.debug(f"[PSM] WS_Clients: {[f'{key}:{ws.id}' for key, ws in self.ws_clients.items()]}")
            res += frontendWS
        
        return res
