import logging
from flask import Flask
from werkzeug.serving import WSGIRequestHandler
import os

from colorama import Fore, Style

def c(text, color, reset='white'):
    colors = {
        'white': Fore.WHITE,
        'cyan': Fore.CYAN,
        'yellow': Fore.YELLOW,
        'red': Fore.RED,
        'magenta': Fore.MAGENTA
    }
    return f"{colors.get(color, '')}{text}{colors.get(reset)}"


class ColorFormatter(logging.Formatter):
    # ANSI escape codes for colors
    COLORS = {
        'DEBUG': "white",
        'INFO': "cyan",
        'WARNING': "yellow",
        'ERROR': "red",
        'CRITICAL': "magenta"
    }

    def format(self, record):
        log_msg = super().format(record)
        
        # Truncate debug log message if longer than 300 characters
        max_length = 300
        if len(log_msg) > max_length and record.levelname == 'DEBUG':
            start = log_msg[:170]
            end = log_msg[-30:]
            omitted_count = len(log_msg) - (len(start) + len(end))
            log_msg = f"{start} {c('... ' + str(omitted_count) + ' characters omitted...', 'yellow')} {end}"
            
        color = self.COLORS.get(record.levelname, '')
        return c(log_msg, color)

class ExternalFilter(logging.Filter): # Filters messages that were sent by [OPCUAClient] or [MQTTClient]
    def __init__(self):
        super().__init__()

    def filter(self, record):
        return record.msg.lower().startswith(('[opcuaclient]', '[mockopcuaclient]', '[mqttclient]'))
    
class InternalFilter(logging.Filter): # Does the oppsite of the ExternalFilter.
    def __init__(self):
        super().__init__()

    def filter(self, record):
        return not record.msg.lower().startswith(('[opcuaclient]', '[mockopcuaclient]', '[mqttclient]'))
    
def setup():
    os.makedirs('logs', exist_ok=True) # create log directory if it doesn't exit yet

    terminal_handler = logging.StreamHandler() # handles messages that will be logged to the terminal
    terminal_handler.setFormatter(ColorFormatter(
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    
    # Internal log file handler
    internal_handler = logging.FileHandler('logs/internal_logs')
    internal_handler.setFormatter(logging.Formatter(
        fmt='%(message)s'
    ))
    internal_handler.addFilter(InternalFilter())

    # External log file handler
    external_handler = logging.FileHandler('logs/external_logs')
    external_handler.setFormatter(logging.Formatter(
        fmt='%(message)s'
    ))
    external_handler.addFilter(ExternalFilter())
    
    level = str(os.getenv('LOG_LEVEL'))
    
    logging.basicConfig(level=level, handlers=[terminal_handler, external_handler, internal_handler])
    
    # Suppress HTTP requests logging
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    logging.getLogger('flask').setLevel(logging.ERROR)
    
    # Suppress OPCUA
    logging.getLogger('asyncua').setLevel(logging.WARNING)