from common import singleton_decorator as s
from backend import mqttClient, opcuaClient
from typing import Any
import asyncio
from asyncio import Task

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
            'factory-overview': { # yes, using a hyphen as a delimiter, not an underscore, because it has to correspond with the page URLs. 
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
            'factory-data': {
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
        if not hasattr(self, 'initialized'):
            self.mqttClient = mqttClient.MqttClient()
            self.opcuaClient = opcuaClient.OPCUAClient()
            self.monitor_tasks: dict[str, Task[Any]] = {}
            self.initialized = True
    
    async def hydrate_page(self, page: str):
        """Called on page load. Makes calls to the backend to make sure all the hydration resources are there. For OPCUA sources, it keeps polling every 0.5s, until it gets data (which is not `None`), then it stops. For MQTT sources, it subscribes, then unsubscribes once it receives a message. Sets the dirty bit.

        Args:
            page (str): Which page to fetch hydration data for.
        """
        
        hydration_tasks = []   
        
        for key, source in self.data.get(page, {}).get('hydrate', {}).items():
            if isinstance(source, self.OPCUASource):
                async def task():
                    while source.value is None: # poll while no value was retrieved
                        source.value = await self.opcuaClient.read(source.node_id)
                        if source.value is not None:
                            source.dirty = True
                            break
                        await asyncio.sleep(0.5)
                        
                hydration_tasks.append(asyncio.create_task(task()))

            elif isinstance(source, self.MQTTSource):
                async def task():
                    def callback(message):
                        source.value = message
                        source.dirty = True
                        self.mqttClient.unsubscribe(source.topic) # unsubscribe when a message is received

                    await self.mqttClient.subscribe(source.topic, callback=callback)
                    
                hydration_tasks.append(asyncio.create_task(task()))
                
        await asyncio.gather(*hydration_tasks)
    
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
        """Called on page load. Stops all previous monitoring tasks and starts monitoring data for the requested page. For OPCUA, it continually monitors the monitoring data for the requested page with a polling period of 0.5s. For MQTT, it subscribes to all the monitoring topics. Sets the dirty bit.

        Args:
            page (str): Which page to poll/subscribe to monitoring data for.
        """
        
        # Cancel any existing monitoring tasks
        if page in self.monitor_tasks:
            await self.stop_monitoring(page)
            
        self.monitor_tasks[page] = []

        # Create monitoring tasks for OPCUA and MQTT sources
        for key, source in self.data.get(page, {}).get('monitor', {}).items():
            if isinstance(source, self.OPCUASource):
                async def poll_opcua_source(source):
                    while True:
                        source.value = await self.opcuaClient.read(source.node_id)
                        source.dirty = True
                        await asyncio.sleep(0.5)

                self.monitor_tasks.append(asyncio.create_task(poll_opcua_source(source)))

            elif isinstance(source, self.MQTTSource):
                def callback(message):
                    source.value = message
                    source.dirty = True

                self.monitor_tasks.append(asyncio.create_task(self.mqttClient.subscribe(source.topic, qos=1, callback=callback)))

        await asyncio.gather(*self.monitor_tasks)  # Await all tasks
    
    async def send_data(self, page: str, key: str, data: Any):
        """Write, or publish data to a source. When the call completes, the result will be available for polling under the given key. Sets the dirty bit.

        Args:
            page (str): Page to store the result for.
            key (str): Key to store the result under.
            data (Any): Data to send.
        """        
        
        if page in self.data:
            for category in self.data[page].values():
                if key in category:
                    source = category[key]
                    if isinstance(source, self.OPCUASource):
                        await self.opcuaClient.write(source.node_id, data)
                    elif isinstance(source, self.MQTTSource):
                        await self.mqttClient.publish(source.topic, data)
    
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
