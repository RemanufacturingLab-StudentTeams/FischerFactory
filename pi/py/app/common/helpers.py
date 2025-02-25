from datetime import datetime, date

def format_time_string(plc_timestamp: str) -> str:
    """Formats the timestamps the PLC produces into a more readable string by cutting off the milliseconds and timezone data.

    Args:
        plc_timestamp (str): PLC timestamp. E.g. "2025-01-23T14:17:13.464080+00:00".

    Returns:
        str: Formatted time string. E.g. "2025/01/23, 14:17:13".
    """    
    if not plc_timestamp:
        return ''
    
    dt = ''
    try: #  ISO 8601 
        dt = datetime.strptime(plc_timestamp, "%Y-%m-%dT%H:%M:%S.%f%z")
    except ValueError: # RFC3339 
        dt = datetime.strptime(plc_timestamp, "%Y-%m-%dT%H:%M:%S%z")
        
    return datetime.strftime(dt, "%m/%d/%Y, %H:%M:%S")
    