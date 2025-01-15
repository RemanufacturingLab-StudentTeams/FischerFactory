from common import MqttClient
import json
from datetime import datetime, date

state = {
    # eg: {'f': {'i': {'order': {ts: <Date>, state: 'IN_PROCESS', type: 'RED'}}}}
}

def _serialize_fallback(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f'Type {type(obj)} is not serializable')

def partial_state_is_leaf(d): # check that a dict does not contain any other dicts or lists
    def is_topic(k: str):
        return k.startswith('/')
    
    return not any(is_topic(k) for k in d.keys())

def push_mqtt(topic: str):
    mqtt_client = MqttClient()
    """Emits data on this topic, if it is a leaf, or on all its subtopics, if not.

    Args:
        topic (str): Topic name, with or without leading slash. Example: 'f/i/state/mpo'
    """
    topic = topic.lstrip('/')
    topic_parts = topic.split('/')
    partial_state = state
    for topic_part in topic_parts:
        partial_state = partial_state.get('/'+topic_part)
        if partial_state is None:
            print(f'!!ERROR!! Could not access {topic_part} while trying to access {topic} in state {state}')
    
    print(f"Sending partial state: {partial_state} over topic {'relay/' + topic}")
    if partial_state_is_leaf(partial_state):
        mqtt_client.publish(topic='relay/' + topic, payload=json.dumps(partial_state, default=_serialize_fallback))
    else:
        for subtopic in partial_state.keys():
            push_mqtt(f'{topic}/{subtopic}')
    
def push_opcua():
    #!TODO
    return
