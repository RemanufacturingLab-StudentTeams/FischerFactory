def no_prefix(s: str):
    """Cuts off the OPCUA DataType prefix off the end of a node ID. Example: `i_code` becomes just `code`.
    Args:
        s (str): The last part of a node ID, without double quote characters. Example: `ldt_ts`.
    """
    
    return s.split('_')[1]

def camel_case(s: str):
    """Convert the last part of a node ID to camelCase (first letter lowercase). 

    Args:
        s (str): Input string. Accepts PascalCase and lowercase. *NO snake_case or kebab-case*.
    """
    
    if s.islower():
        return s
    return s[0].lower() + s[1:]

def convert(s):
    return camel_case(no_prefix(s))

def state_station(station: str):
    """Generates the base relay mapping for the state of a component (DSI, DSO, MPO, SLD, VGR, HBW)

    Args:
        station (str): Either mpo, sld, vgr or hbw.
    """    
    
    node_id_root = f'"gtyp_Interface_Dashboard"."Subscribe"."State_{station.upper()}"'
    return {
            no_prefix(e): f'{node_id_root}."{e}"'
            for e in ['i_code', 'ldt_ts', 's_description', 's_station', 's_target', 'x_active', 'x_error', 's_errorMessage']
        }
    
class RelaySubNode:
    def __init__(self, sub_node_id: str, payload_map: list[str | dict]):
        self.sub_node = sub_node_id,
        self.payload_map = payload_map
    
class RelayHistoryNode:
    def __init__(self, max_length: int):
        self.max_length = max_length
    
class RelayTopic:
    def __init__(self, topic_map: dict, payload_map: list[str | dict | RelaySubNode | RelayHistoryNode], relay_interval=1):
        self.topic_map = topic_map
        self.payload_map = payload_map
        self.relay_interval = relay_interval