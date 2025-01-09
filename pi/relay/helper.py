from mappings import special_rules
from asyncua import ua, Node
from datetime import datetime

def _no_prefix(s: str):
    """Cuts off the OPCUA DataType prefix off the end of a node ID. Example: `i_code` becomes just `code`.
    Args:
        s (str): The last part of a node ID, without double quote characters. Example: `ldt_ts`.
    """
    
    if s.find('_') == -1: 
        return s
    return ''.join(s.split('_')[1:]) # i know it's unreadable but i promise this works bro

def _camel_case(s: str):
    """Convert the last part of a node ID to camelCase (first letter lowercase). 

    Args:
        s (str): Input string. Accepts PascalCase and lowercase. *NO snake_case or kebab-case*.
    """
    
    if s.islower():
        return s
    return s[0].lower() + s[1:]

def _convert(s):
    return _camel_case(_no_prefix(s.strip('"')))

# Helper functions for converting field names
def name_to_mqtt(name: str):
    for rule in special_rules:
        if rule.ORIGINAL == name:
            name = rule.MEANS
    return _convert(name)

async def get_datatype_as_str(node: Node) -> str:
    """Determine the data type from the node ID prefix."""
    
    datatype_node_ids: dict[int, str] = { # all the primitive types
        1: 'Boolean',
        3014: 'String',
        3002: 'Word',  # 16 bits
        13: 'DateTime',
        4: 'Int16',
        6: 'Int32',
        10: 'Float'
    }
    
    dt = (await node.read_data_type()).Identifier
    try:
        return datatype_node_ids[dt]
    except KeyError:
        # Nested type
        return 'Nested'
    
def value_to_ua(value: any, data_type: str) -> object:
    """Convert the input value to the correct UA type."""
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
    
def value_to_mqtt(value: any, data_type: str) -> object:
    """Convert the input value to the correct MQTT type (which are just standard Python types)."""
    if data_type == 'Boolean':
        # Convert to Python boolean
        if isinstance(value, (bool, int)):
            return bool(value)
        else:
            raise ValueError(f"Invalid value for Boolean: {value}")

    elif data_type == 'Int16':
        # Convert to Python int (16-bit range check)
        if isinstance(value, (int, float)) and -32768 <= int(value) <= 32767:
            return int(value)
        else:
            raise ValueError(f"Value out of range for Int16: {value}")

    elif data_type == 'Int32':
        # Convert to Python int (32-bit range check)
        if isinstance(value, (int, float)) and -2147483648 <= int(value) <= 2147483647:
            return int(value)
        else:
            raise ValueError(f"Value out of range for Int32: {value}")

    elif data_type == 'Float':
        # Convert to Python float
        try:
            return float(value)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid value for Float: {value}")

    elif data_type == 'DateTime':
        # Convert to Python datetime
        if isinstance(value, datetime):
            return value
        else:
            raise ValueError(f"Invalid datetime format for DateTime: {value}")

    elif data_type == 'String':
        # Convert to Python string
        try:
            return str(value)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid value for String: {value}")

    elif data_type == 'Word':  # 16-bit unsigned integer
        # Convert to Python int (0 to 65535 range check)
        if isinstance(value, (int, float)) and 0 <= int(value) <= 65535:
            return int(value)
        else:
            raise ValueError(f"Value out of range for Word: {value}")

    else:
        raise ValueError(f"Unsupported data type: {data_type}")