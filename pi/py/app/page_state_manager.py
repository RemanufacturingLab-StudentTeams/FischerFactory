from common import singleton_decorator as s
from backend import mqttClient, opcuaClient
from typing import Any
import asyncio

@s.singleton
class PageStateManager:
    '''Manages and fetches state from external sources (MQTT or OPCUA). It is more or less a buffer, so that the results of async calls can be made accessible to Dash callbacks.
    '''
    
    class OPCUASource:   
        value: Any = None
        dirty = False # Whether it has changed since the last time it was accessed. 

        def __init__(self, node_id: str):
            self.node_id = node_id
            self.monitor_tasks = {}
            
    class MQTTSource:
        value: Any = None
        dirty = False # Whether it has changed since the last time it was accessed. 

        def __init__(self, topic: str):
            self.topic = topic
    
    data = {
            'factory_overview': {
                'hydrate': {
                    'plc_version': OPCUASource('ns=3;s="gtyp_Setup"."r_Version_SPS"')
                },
                'monitor': {
                    'rack_workpieces': OPCUASource('ns=3;s="gtyp_HBW"."Rack_Workpiece"'),
                    'turtlebot_current_state': MQTTSource('Turtlebot/CurrentState')
                },
                'user': {
                    'clean_rack': OPCUASource('ns=3;s="gtyp_Setup"."x_Clean_Rack_HBW"')
                }
            },
            'factory_data': {
                'hydrate': {
                    
                },
                'monitor': {
                    'state_sld': MQTTSource('f/i/state/sld')
                },
                'user': {
                    
                }
            }
        }
    
    def __init__(self):
        if not self.initialized:
            self.mqttClient = mqttClient.MqttClient()
            self.opcuaClient = opcuaClient.OPCUAClient()
            self.monitor_tasks = {}
            self.initialized = True
    
    async def hydrate_page(self, page: str):
        """Called on page load. Makes calls to the backend to make sure all the hydration resources are there. For OPCUA sources, it keeps polling every 0.5s, until it gets data (which is not `None`), then it stops. For MQTT sources, it subscribes, then unsubscribes once it receives a message. Sets the dirty bit.

        Args:
            page (str): Which page to fetch hydration data for.
        """        
        
        for key, source in self.data.get(page, {}).get('hydrate', {}).items():
            if isinstance(source, self.OPCUASource):
                while source.value is None:
                    source.value = await self.opcuaClient.read(source.node_id)
                    if source.value is not None:
                        source.dirty = True
                        break
                    await asyncio.sleep(0.5)

            elif isinstance(source, self.MQTTSource):
                def callback(message):
                    source.value = message
                    source.dirty = True

                await self.mqttClient.subscribe(source.topic, qos=1, callback=callback)
    
    async def stop_monitoring(self, page: str):
        """Stop all monitoring tasks for the specified page."""
        if page in self.monitor_tasks:
            for task in self.monitor_tasks[page]:
                task.cancel()
                try:
                    await task  # Ensure the task is properly canceled
                except asyncio.CancelledError:
                    pass
            del self.monitor_tasks[page]  # Remove the page from the tracking dictionary

    async def monitor_page(self, page: str):
        """Called on page load. For OPCUA, it continually monitors the monitoring data for the requested page with a polling period of 0.5s. For MQTT, it subscribes to all the monitoring topics. Sets the dirty bit.

        Args:
            page (str): Which page to poll/subscribe to monitoring data for.
        """
        
        # Cancel any existing monitoring tasks
        if page in self.monitor_tasks:
            await self.stop_monitoring(page)

        tasks = []

        # Create monitoring tasks for OPCUA and MQTT sources
        for key, source in self.data.get(page, {}).get('monitor', {}).items():
            if isinstance(source, self.OPCUASource):
                async def poll_opcua_source(source):
                    while True:
                        source.value = await self.opcuaClient.read(source.node_id)
                        source.dirty = True
                        await asyncio.sleep(0.5)

                tasks.append(asyncio.create_task(poll_opcua_source(source)))

            elif isinstance(source, self.MQTTSource):
                def callback(message):
                    source.value = message
                    source.dirty = True

                tasks.append(asyncio.create_task(self.mqttClient.subscribe(source.topic, qos=1, callback=callback)))

        # Store the tasks for the page
        self.monitor_tasks[page] = tasks
        await asyncio.gather(*tasks)  # Await all tasks
    
    def set_data(self, page: str, key: str, data: Any):
        """Can, for instance, be called when a user-instigated async call completes. Sets the dirty bit.

        Args:
            page (str): Page to store the data for.
            key (str): Key to store the data under.
            data (Any): Data to store.
        """        
        
        if page in self.data:
            for category in self.data[page].values():
                if key in category:
                    source = category[key]
                    source.value = data
                    source.dirty = True
    
    def get_data(self, page: str, key: str) -> Any:
        """Accesses data for a specific page, based on a key. Resets the dirty bit.

        Args:
            page (str): Which page to get data for.
            key (str): The key this data is under. For example: `plc_version`.
        """        
    
        if page in self.data:
            for category in self.data[page].values():
                if key in category:
                    source = category[key]
                    source.dirty = False
                    return source.value
        return None
