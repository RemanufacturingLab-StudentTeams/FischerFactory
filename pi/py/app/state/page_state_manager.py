from common import config
from common import singleton_decorator as s
from backend import mqttClient, opcuaClient, mockOpcuaClient
from typing import Any
import asyncio
import logging
from asyncio import Task
from state import state_data_schema


@s.singleton
class PageStateManager:
    '''Manages and fetches state from external sources (MQTT or OPCUA). It is more or less a buffer, so that the results of async calls can be made accessible to Dash callbacks. It is a singleton.
    '''
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.mqttClient = mqttClient.MqttClient()
            self.opcuaClient = opcuaClient.OPCUAClient() 
            self.monitor_tasks: list[Task[Any]] = []
            self.global_monitor_tasks: list[Task[Any]] = []
            self.data = state_data_schema._data
    
            self.initialized = True
    
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
        
        logging.debug(f'[PSM] Monitoring page: {page} with data: {[k for k, s in self.data.get(page, {}).get("monitor", {}).items()]}')

        # Create monitoring tasks for OPCUA and MQTT sources
        for key, topic in self.data.get(page, {}).items():
            def callback(message):
                config.socketio.emit(namespace=f'{page}/{key}', args=message)
            if is_global:
                self.global_monitor_tasks.append(asyncio.create_task(self.mqttClient.subscribe(topic, qos=1, callback=callback)))
            self.monitor_tasks.append(asyncio.create_task(self.mqttClient.subscribe(topic, qos=1, callback=callback)))

        if is_global:
            await asyncio.gather(*self.global_monitor_tasks)
        
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
