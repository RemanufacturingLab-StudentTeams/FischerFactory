import logging
from flask import Flask
from werkzeug.serving import WSGIRequestHandler

class ColorFormatter(logging.Formatter):
    # ANSI escape codes for colors
    COLORS = {
        'DEBUG': "\033[0;37m",    # White
        'INFO': "\033[0;36m",     # Cyan
        'WARNING': "\033[0;33m",  # Yellow
        'ERROR': "\033[0;31m",    # Red
        'CRITICAL': "\033[1;41m", # White on Red background
        'RESET': "\033[0m"        # Reset color
    }

    def format(self, record):
        log_msg = super().format(record)
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        return f'{color}{log_msg}{reset}'

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