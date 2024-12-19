from mappings import special_rules

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

# Helper functions for converting field names
def convert_to_opcua_format(name: str):
    for rule in special_rules:
        if rule.ORIGINAL == name:
            return rule.MEANS
    if name[0].islower():
        return f"s_{name.capitalize()}"
    return name

def convert_to_mqtt_format(name: str):
    for rule in special_rules:
        if rule.MEANS == name:
            return rule.ORIGINAL
    if name.startswith("s_"):
        return name[2].lower() + name[3:]
    return name

def _get_data_type_from_node_id(node_id: str) -> str:
    """Determine the data type from the node ID prefix."""
    
    # Hardcoded VariantTypes for node id's that do not fit the standard.
    match node_id.split('.')[-1].strip('\"'):
        case 'OvenTime':
            return 'Int32'
        case 'SawTime':
            return 'Int32'
        case 'DoOven':
            return 'Boolean'
        case 'DoSaw':
            return 'Boolean'
        case 'track_puck':
            return 'String'
    
    prefixes = {
        'x': 'Boolean',
        's': 'String',
        'w': 'Word',  # 16 bits
        'ldt': 'DateTime',
        'i': 'Int16',
        'di': 'Int32',
        'r': 'Float'
    }
    for prefix, data_type in prefixes.items():
        if node_id.split('.')[-1].strip('\"').split('_')[0] == prefix:
            return data_type
    raise ValueError(f"Unknown node ID prefix: {node_id[:2]}")
    
def _convert_to_correct_type(value: any, data_type: str) -> object:
    """Convert the input value to the correct type."""
    if data_type == 'Boolean':
        return ua.DataValue(ua.Variant(value, ua.VariantType.Boolean))
    elif data_type == 'Int16':
        return ua.DataValue(ua.Variant(value, ua.VariantType.Int16))
    elif data_type == 'Int32':
        return ua.DataValue(ua.Variant(value, ua.VariantType.Int32))
    elif data_type == 'Float':
        return ua.DataValue(ua.Variant(value, ua.VariantType.Float))
    elif data_type == 'DateTime':
        if isinstance(value, datetime):
            return ua.DataValue(ua.Variant(value, ua.VariantType.DateTime))
        else:
            raise ValueError(f"Invalid datetime format for {data_type}")
    elif data_type == 'String':
        return ua.DataValue(ua.Variant(value, ua.VariantType.String))
    elif data_type == 'Word':  # 16 bits
        return int(value) & 0xFFFF
    else:
        raise ValueError(f"Unsupported data type: {data_type}")