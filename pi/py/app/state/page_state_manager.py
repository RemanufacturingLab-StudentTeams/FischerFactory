from common import config
from common import singleton_decorator as s
from backend import mqttClient, opcuaClient, mockOpcuaClient
from typing import Any
import asyncio
import logging
from asyncio import Task
from state.state_data_sources import OPCUASource, MQTTSource
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
            self.data = state_data_schema._data
            self.initialized = True
    
    async def hydrate_page(self, page: str):
        """Called on page load. Makes calls to the backend to make sure all the hydration resources are there. For OPCUA sources, it keeps polling every 0.5s, until it gets data (which is not `None`), then it stops. For MQTT sources, it subscribes, then unsubscribes once it receives a message. Sets the dirty bit.

        Args:
            page (str): Which page to fetch hydration data for.
        """
        logging.debug(f'[PSM] Hydrating page: {page} with data: {[k for k, s in self.data.get(page, {}).get("hydrate", {}).items()]}')
        
        hydration_tasks = []   
        
        for key, source in self.data.get(page, {}).get('hydrate', {}).items():
            if isinstance(source, OPCUASource):
                async def task():
                    while source.value is None: # poll while no value was retrieved
                        v = await self.opcuaClient.read(source.node_id)
                        if v is not None:
                            source.set_value(v)
                            break
                        await asyncio.sleep(0.5)
                        
                hydration_tasks.append(asyncio.create_task(task()))

            elif isinstance(source, MQTTSource):
                async def task():
                    def callback(message):
                        source.set_value(message)
                        self.mqttClient.unsubscribe(source.topic) # unsubscribe when a message is received

                    await self.mqttClient.subscribe(source.topic, callback=callback)
                    
                hydration_tasks.append(asyncio.create_task(task()))
                
        await asyncio.gather(*hydration_tasks)
    
    async def stop_monitoring(self):
        """Stop all monitoring tasks."""
        logging.debug(f'[PSM] Stopping all monitoring tasks')
        
        for task in self.monitor_tasks:
            try:
                if not task.done:
                    task.cancel()
                await task  # Ensure the task is properly canceled
            except asyncio.CancelledError as e: # this is actually fine, it should give a CancelledError because it was cancelled
                pass
        self.monitor_tasks = []

    async def monitor_page(self, page: str):
        """Called on page load. Stops all previous monitoring tasks and starts monitoring data for the requested page. For OPCUA, it continually monitors the monitoring data for the requested page with a polling period of 0.5s. For MQTT, it subscribes to all the monitoring topics. Sets the dirty bit.

        Args:
            page (str): Which page to poll/subscribe to monitoring data for.
        """
        # Cancel any existing monitoring tasks
        if page != 'global':
            await self.stop_monitoring()
        
        logging.debug(f'[PSM] Monitoring page: {page} with data: {[k for k, s in self.data.get(page, {}).get("monitor", {}).items()]}')

        # Create monitoring tasks for OPCUA and MQTT sources
        for key, source in self.data.get(page, {}).get('monitor', {}).items():
            
            if isinstance(source, OPCUASource):
                async def poll_opcua_source(source):
                    while True:
                        v = await self.opcuaClient.read(source.node_id)
                        source.set_value(v)
                        await asyncio.sleep(0.5)

                self.monitor_tasks.append(asyncio.create_task(poll_opcua_source(source)))

            elif isinstance(source, MQTTSource):
                def callback(message):
                    source.set_value(message)

                self.monitor_tasks.append(asyncio.create_task(self.mqttClient.subscribe(source.topic, qos=1, callback=callback)))

        await asyncio.gather(*self.monitor_tasks)  # Await all tasks
    
    async def send_data(self, page: str, keys_and_data: dict):
        """Write or publish multiple data items to a source. When the call completes, the results will be 
        available for polling under the given keys. Sets the dirty bit for each source.

        Args:
            page (str): Page to store the results for. Use a hyphen as a delimiter. Example: `factory-data`.
            keys_and_data (dict): A dictionary where keys are the data keys and values are the data to send. Example: {'order_do_oven': True, 'order_bake_time': 4000}.
        """
        if page not in self.data:
            return
        
        logging.debug(f'[PSM] Sending user data: {keys_and_data}')
        tasks = []  # List to hold async tasks for concurrent execution
        
        async def task(key, data, source):
            if isinstance(source, OPCUASource):
                await self.opcuaClient.write(source.node_id, data)
            elif isinstance(source, MQTTSource):
                await self.mqttClient.publish(source.topic, data)
            source.value = data
            source.dirty = True
        
        for category in self.data[page].values():
            for key, data in keys_and_data.items():
                if key in category:
                    source = category[key]
                    tasks.append(task(key, data, source))
        
        await asyncio.gather(*tasks)
    
    def get(self, page: str, key: str, return_none_if_clean=True) -> Any:
        """Accesses data for a specific page, based on a key. Resets the dirty bit.

        Args:
            page (str): Which page to get data for. Format is pathname without leading '/', so with hyphen delimiter. Example: `factory-overview`.
            key (str): The key this data is under. For example: `plc_version`.
            return_none_if_clean (bool): Default True. If set to True, it will return None if nothing changed since last time it was called. Useful to catch with PreventUpdate for performance to prevent unnecessary UI updates.
            
        Returns:
            (Any): Returns `None` if the value is clean. Please raise `PreventUpdate` in the callbacks in case it returns None.
        """        
    
        if page in self.data:
            for category in self.data[page].values():
                if key in category:
                    source = category[key]
                    
                    if source.dirty: 
                        source.dirty = False
                        return source.value
                    else:
                        if return_none_if_clean:
                            break
                        else:
                            return source.value # return even though it is clean    
        return None
    
    def dirty_all(self, page):
        """Gets all sources on this page to dirty.

        Args:
            page (str): Page name, with hyphen delimiter.
        """        
        if page in self.data:
            for category in self.data[page].values():
                for key in category:
                    category[key].dirty = True
