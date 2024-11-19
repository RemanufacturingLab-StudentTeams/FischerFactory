from common import singleton_decorator as s
from backend import mqttClient, opcuaClient
from typing import Any
import asyncio
import logging
from asyncio import Task

class OPCUASource:   
    def __init__(self, node_id: str):
        self.value: Any = None
        self.dirty: bool = False # Whether it has changed since the last time it was accessed. 
        self.node_id = node_id
        self.monitor_tasks = {}
    
    def set_value(self, v: Any):
        if v is None:
            return
        if v != self.value:
            self.dirty = True
            self.value = v
        
class MQTTSource:
    def __init__(self, topic: str):
        self.value: Any = None
        self.dirty: bool = False # Whether it has changed since the last time it was accessed. 
        self.topic = topic
        
    def set_value(self, v: Any):
        if v is not None and v != self.value:
            self.dirty = True
            self.value = v if self.value is None else self.value | v # dict union operator, so existing values are not reset
                
@s.singleton
class PageStateManager:
    '''Manages and fetches state from external sources (MQTT or OPCUA). It is more or less a buffer, so that the results of async calls can be made accessible to Dash callbacks. It is a singleton.
    '''
        
    data = {
            'factory-overview': { # yes, using a hyphen as a delimiter, not an underscore, because it has to correspond with the page URLs. 
                'hydrate': {
                    'plc_version': OPCUASource('ns=3;s="gtyp_Setup"."r_Version_SPS"')
                },
                'monitor': {
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
            },
            'dashboard-customer': {
                'hydrate': {
                    
                },
                'monitor': {
                    f'rack_workpiece_[{x},{y}]_{e}': OPCUASource(f'ns=3;s="gtyp_HBW"."Rack_Workpiece"[{x},{y}]."{e}"')
                    for x in range(3) 
                    for y in range(3) 
                    for e in ['s_id', 's_state', 's_type']
                },
                'user': {
                    's_type': OPCUASource('ns=3;s="gtyp_Interface_Dashboard"."Publish"."OrderWorkpieceButton"."s_type"'),
                    'order_oven_time': OPCUASource('ns=3;s="gtyp_Interface_Dashboard"."Publish"."OrderWorkpieceButton"."Workpiece_Parameters"."OvenTime"'),
                    'order_do_oven': OPCUASource('ns=3;s="gtyp_Interface_Dashboard"."Publish"."OrderWorkpieceButton"."Workpiece_Parameters"."DoOven"'),
                    'order_saw_time': OPCUASource('ns=3;s="gtyp_Interface_Dashboard"."Publish"."OrderWorkpieceButton"."Workpiece_Parameters"."SawTime"'),
                    'order_do_saw': OPCUASource('ns=3;s="gtyp_Interface_Dashboard"."Publish"."OrderWorkpieceButton"."Workpiece_Parameters"."DoSaw"'),
                    'order_ldt_ts': OPCUASource('ns=3;s="gtyp_Interface_Dashboard"."Publish"."OrderWorkpieceButton"."ldt_ts"'),
                }
            }
        }
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.mqttClient = mqttClient.MqttClient()
            self.opcuaClient = opcuaClient.OPCUAClient()
            self.monitor_tasks: list[Task[Any]] = []
            self.initialized = True
    
    async def hydrate_page(self, page: str):
        """Called on page load. Makes calls to the backend to make sure all the hydration resources are there. For OPCUA sources, it keeps polling every 0.5s, until it gets data (which is not `None`), then it stops. For MQTT sources, it subscribes, then unsubscribes once it receives a message. Sets the dirty bit.

        Args:
            page (str): Which page to fetch hydration data for.
        """
        
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
        logging.debug(f'[PSM] Monitoring page: {page}')
        
        # Cancel any existing monitoring tasks
        await self.stop_monitoring()

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
                    if isinstance(source, OPCUASource):
                        await self.opcuaClient.write(source.node_id, data)
                    elif isinstance(source, MQTTSource):
                        await self.mqttClient.publish(source.topic, data)
    
    def get_data(self, page: str, key: str) -> Any:
        """Accesses data for a specific page, based on a key. Resets the dirty bit.

        Args:
            page (str): Which page to get data for. Format is pathname without leading '/', so with hyphen delimiter. Example: `factory-overview`.
            key (str): The key this data is under. For example: `plc_version`.
            
        Returns:
            (Any): Returns `None` if the value is clean. Please raise `PreventUpdate` in the callbacks in case it returns None.
        """        
    
        if page in self.data:
            for category in self.data[page].values():
                if key in category:
                    source = category[key]
                    if source.dirty: # return None if value is clean
                        source.dirty = False
                        return source.value
                    else:
                        break
        return None
