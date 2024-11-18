from common import singleton_decorator as s
from backend import mqttClient, opcuaClient

@s.singleton
class PageStateManager:
    '''Manages and fetches state from external sources (MQTT or OPCUA). It is more or less a buffer, so that the results of async calls can be made accessible to Dash callbacks.
    '''
    
    class OPCUASource:
        value = None
        dirty = False

        def __init__(self, node_id: str):
            self.node_id = node_id
            
    class MQTTSource:
        value = None
        dirty = False

        def __init__(self, topic: str):
            self.topic = topic
    
    mqttClient = mqttClient.MqttClient()
    opcuaClient = opcuaClient.OPCUAClient()
    
    data = {
            'factory_overview': {
                'hydrate': {
                    'plc-version': OPCUASource('ns=3;s="gtyp_Setup"."r_Version_SPS"')
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
    
    async def hydrate_page(page: str):
        return
    
    async def monitor_page(page: str):
        return
    
    def buffer_user_data(page: str, key: str):
        return
    
    def get_data(self):
        return self.data
