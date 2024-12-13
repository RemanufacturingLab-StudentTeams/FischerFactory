from typing import Any
import os

# Classes that are part of the state_data_schema, which are always available, from a synchronous context via the PageStateManager.
class OPCUASource:   
    def _generate_mock_value(self):
        self.mock_value = ''

    def __init__(self, node_id: str, return_none_if_clean=True):
        self.value: Any = None
        self.dirty: bool = False # Whether it has changed since the last time it was accessed. This could be because of an external event, such as in the case of monitoring and hydration data, or because of a user-initiated mutation.
        self.node_id = node_id
    
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