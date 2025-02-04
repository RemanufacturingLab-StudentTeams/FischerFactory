import logging
from flask import Flask
from werkzeug.serving import WSGIRequestHandler
import os
from collections import deque
from dash import html
import re 

from colorama import Fore, Style

frontend_log: deque[html.Tr] = deque(maxlen=1000)

class FrontEndLogHandler(logging.Handler):
    def emit(self, record):
        # Only emit if the log level is WARNING, INFO, or ERROR
        if record.levelno in [logging.WARNING, logging.INFO, logging.ERROR]:
            try:
                log_entry = self.format(record)
                # Append the log entry to the deque (automatically removes oldest when maxlen is exceeded)
                frontend_log.append(html.Tr(
                    log_entry
                ))
            except Exception:
                self.handleError(record)

def c(text, color, reset='white'):
    colors = {
        'white': Fore.WHITE,
        'cyan': Fore.CYAN,
        'yellow': Fore.YELLOW,
        'red': Fore.RED,
        'magenta': Fore.MAGENTA
    }
    return f"{colors.get(color, '')}{text}{colors.get(reset)}"

def frontend_c(text: str, color) -> html.Span:
    if color != 'black':
        return html.Span(text, style={'color': color, 'background-color': 'black'})
    return html.Span(text, style={'color': color})

COLORS = {
    'DEBUG': "white",
    'INFO': "cyan",
    'WARNING': "yellow",
    'ERROR': "red",
    'CRITICAL': "magenta"
}

class ColorFormatter(logging.Formatter):

    def format(self, record):
        log_msg = super().format(record)
        
        # Truncate debug log message if longer than 300 characters
        max_length = 300
        if len(log_msg) > max_length and record.levelname == 'DEBUG':
            start = log_msg[:170]
            end = log_msg[-30:]
            omitted_count = len(log_msg) - (len(start) + len(end))
            log_msg = f"{start} {c('... ' + str(omitted_count) + ' characters omitted...', 'yellow')} {end}"
            
        color = COLORS.get(record.levelname, '')
        return c(log_msg, color)

class FrontEndFormatter(logging.Formatter):
    def format(self, record):
        log_msg = super().format(record)
            
        # get rid of ANSI codes
        log_msg = re.sub(r'\x1b\[[0-9;]*m', '', log_msg)
            
        color = 'black' if record.levelname == 'INFO' else COLORS.get(record.levelname, '')
        return frontend_c(log_msg, color)

class ExternalFilter(logging.Filter): # Filters messages that were sent by [OPCUAClient] or [MQTTClient]
    def __init__(self):
        super().__init__()

    def filter(self, record):
        return str(record.msg).lower().startswith(('[opcuaclient]', '[mockopcuaclient]', '[mqttclient]'))
    
class InternalFilter(logging.Filter): # Does the oppsite of the ExternalFilter.
    def __init__(self):
        super().__init__()

    def filter(self, record):
        return not (str(record.msg).lower().startswith(('[opcuaclient]', '[mockopcuaclient]', '[mqttclient]')))
    
def setup():
    os.makedirs('logs', exist_ok=True) # create log directory if it doesn't exit yet

    log_messages = os.getenv('LOG_MESSAGES')

    terminal_handler = logging.StreamHandler() # handles messages that will be logged to the terminal
    terminal_handler.setFormatter(ColorFormatter(
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    if log_messages == 'FALSE' or log_messages == 'FILE':
        terminal_handler.addFilter(InternalFilter())
    
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
    
    # Frotend log handler
    frontend_handler = FrontEndLogHandler()
    frontend_handler.setFormatter(FrontEndFormatter())
    frontend_handler.addFilter(InternalFilter())
    
    handlers = []
    handlers.append(terminal_handler)
    handlers.append(internal_handler)
    handlers.append(frontend_handler)
    if log_messages == 'TRUE' or log_messages == 'FILE':
        handlers.append(external_handler)
    
    level = str(os.getenv('LOG_LEVEL'))
    logging.basicConfig(level=level, handlers=handlers)
    
    # Suppress HTTP requests logging
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    logging.getLogger('flask').setLevel(logging.ERROR)
    
    # Suppress OPCUA
    logging.getLogger('asyncua').setLevel(logging.WARNING)
    logging.getLogger('websockets').setLevel(logging.WARNING)