from datetime import datetime, date

def format_time_string(plc_timestamp: str) -> str:
    """Formats the timestamps the PLC produces (ISO 8601 or FRC3339) into a more readable string by cutting off the milliseconds and timezone data.

    Args:
        plc_timestamp (str): PLC timestamp. E.g. "2025-01-23T14:17:13.464080+00:00Z".

    Returns:
        str: Formatted time string. E.g. "2025/01/23, 14:17:13".
    """    
    if not plc_timestamp:
        return ''
    
    if 'Z' in plc_timestamp:
        plc_timestamp = plc_timestamp.replace('Z', '')
    
    if '+' in plc_timestamp:
        plc_timestamp = plc_timestamp.split('+')[0]
        
    dt = ''
    try: #  ISO 8601 
        dt = datetime.strptime(plc_timestamp, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError: # RFC3339 
        dt = datetime.strptime(plc_timestamp, "%Y-%m-%dT%H:%M:%S")
        
    return datetime.strftime(dt, "%m/%d/%Y, %H:%M:%S")
    