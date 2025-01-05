"""Hey, modularity! This module is here so that import configurations and resources are accessible anywhere in the program, and to fix circular dependencies that happened when this was in `app/app.py`. 
"""

from dash import Dash
from flask_socketio import SocketIO
from flask import Flask

server = Flask(__name__)
socketio = SocketIO(server)
app = Dash(__name__,
                server=server,
                external_stylesheets=[
                    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"
                    ],
                use_pages=True,
                pages_folder='../pages',
                assets_folder='../assets',
                prevent_initial_callbacks=True
                )

mode = None
"""Specifies what mode the program is running in. Either 'dev', 'prod', or 'test'. Set in `app/app.py`."""

# Exports
__all__ =["app", "mode", "server", "socketio"]