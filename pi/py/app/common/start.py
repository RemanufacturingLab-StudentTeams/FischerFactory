from flask import Flask
from flask_socketio import SocketIO
from dash import Dash

server = Flask(__name__)
socketio = SocketIO(server) 
app = Dash(__name__, 
                external_stylesheets=[
                    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"
                    ],
                use_pages=True,
                pages_folder='../pages',
                assets_folder='../assets',
                server=server
                )

# Exports
__all__ = ["server", "socketio", "app"]