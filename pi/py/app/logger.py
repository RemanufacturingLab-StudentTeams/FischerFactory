import logging
from flask import Flask
from werkzeug.serving import WSGIRequestHandler

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
        color = self.COLORS.get(record.levelname, '')
        return c(log_msg, color)

def setup():
    handler = logging.StreamHandler()
    handler.setFormatter(ColorFormatter(
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    
    logging.basicConfig(level=logging.DEBUG, handlers=[handler])
    
    # Suppress HTTP requests logging
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    logging.getLogger('flask').setLevel(logging.ERROR)