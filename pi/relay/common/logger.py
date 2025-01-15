import logging
import os

from colorama import Fore

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
    
def setup():
    terminal_handler = logging.StreamHandler() # handles messages that will be logged to the terminal
    terminal_handler.setFormatter(ColorFormatter(
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    
    level = str(os.getenv('LOG_LEVEL'))
    logging.basicConfig(level=level, handlers=[terminal_handler])
    
    # Suppress OPCUA
    logging.getLogger('asyncua').setLevel(logging.WARNING)