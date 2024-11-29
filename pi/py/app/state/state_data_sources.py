from typing import Any
import os

class OPCUASource:   
    def _generate_mock_value(self):
        self.mock_value = ''

    def __init__(self, node_id: str):
        self.value: Any = None
        self.dirty: bool = False # Whether it has changed since the last time it was accessed. 
    
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