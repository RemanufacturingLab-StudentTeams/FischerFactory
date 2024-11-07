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
        
        # Truncate debug log message if longer than 200 characters
        max_length = 200
        if len(log_msg) > max_length and record.levelname == 'DEBUG':
            start = log_msg[:170]
            end = log_msg[-30:]
            omitted_count = len(log_msg) - (len(start) + len(end))
            log_msg = f"{start} {c('... ' + str(omitted_count) + ' characters omitted...', 'yellow')} {end}"
            
        color = self.COLORS.get(record.levelname, '')
        return c(log_msg, color)

def setup():
    handler = logging.StreamHandler()
    handler.setFormatter(ColorFormatter(
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    
    level = str(os.getenv('LOG_LEVEL'))
    
    logging.basicConfig(level=level, handlers=[handler])
    
    # Suppress HTTP requests logging
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    logging.getLogger('flask').setLevel(logging.ERROR)
    
    # Suppress OPCUA
    logging.getLogger('asyncua').setLevel(logging.WARNING)