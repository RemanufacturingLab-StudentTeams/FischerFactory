import pprint
from dash import dcc, html, Input, Output, Dash, ALL
import logger
from dotenv import load_dotenv
import os, argparse
from backend import mqttClient
from threading import Thread
from common import runtime_manager
from state import PageStateManager
from common import config
import asyncio
import websockets
from websockets.asyncio.server import Server as WebSocketServer
from websockets.asyncio.server import ServerConnection
from websockets.http11 import Request
from threading import Thread
import json

def init_dash() -> Dash:
    return Dash(__name__,
        external_stylesheets=[
            "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"
        ],
        external_scripts=[
            "https://cdn.socket.io/4.0.0/socket.io.min.js"
        ],
        use_pages=True,
        prevent_initial_callbacks=True
        )    

async def generate_global_layout(app: Dash) -> None:    
    from global_layout import layout
    app.layout = await layout()

connections: dict[ServerConnection] = {}

def start_ws():
    import os # Cannot put this on the top of the file because it needs to be imported after the main function loads the environment variables
    import logging # same here, it needs to be set up first 
    from backend import MqttClient
    
    async def websocket_handler(conn: ServerConnection):
        """Handles WebSocket connections and messages."""
        async for message in conn:
            logging.debug(f"[WS_SERVER] Received: {message}")
    
    def request_handler(conn: ServerConnection, req: Request):
        logging.debug(f'[WS_SERVER] Incoming request on path {req.path}')
        if connections.get(req.path) is None:
            connections[req.path] = conn
            mqttClient = MqttClient()
            async def send_to_frontend(msg, conn=conn, path=req.path):
                try:                   
                    conn.send(json.dumps(msg))
                    logging.debug(f'[WS_SERVER] Sent message {msg} to FrontEnd WebSocket {path}')
                except Exception as e:
                    logging.error(f'[WS_SERVER] Failed to send message to frontend WebSocket {path}')
            psm = PageStateManager()
            psm.monitor_tasks.append(asyncio.create_task(mqttClient.subscribe(req.path, callback=send_to_frontend)))
    
    async def run_server():
        logging.info(f"Starting WebSocket server on ws://localhost:{os.getenv('WS_PORT')}...")
        async with websockets.serve(websocket_handler, "localhost", 8765, process_request=request_handler):
            logging.info("WebSocket server is running.")
            await asyncio.Future()
    
    asyncio.run(run_server())

async def main():
    parser = argparse.ArgumentParser(description="Run the application.")
    parser.add_argument("--dev", action="store_true", help="Run in development mode")
    config.mode = 'dev' if parser.parse_args().dev else 'prod'
    os.environ.clear()

    # Load environment variables
    load_dotenv(dotenv_path=f".env.{config.mode}")
    print(
        f"Running in \033[0;33m{config.mode} mode\033[0m with environment variables:"
    )
    pprint.pprint(os.environ.copy())
    logger.setup()

    # Initialize the MQTT client
    mqtt = mqttClient.MqttClient()
    await mqtt.connect()
    
    # Start the WebSocket server in a separate Thread
    Thread(target=start_ws, daemon=True).start()
    
    app = init_dash()
    
    # Register pages
    from pages.factory_overview import register as register_overview
    await register_overview()
    from pages.dashboard_customer import register as register_dashboard_customer
    await register_dashboard_customer()
    
    # Init the Dash app
    await generate_global_layout(app)
    
    # Launch the app
    app.run(
        dev_tools_hot_reload=(config.mode == 'dev'), 
        debug=False, port=os.getenv("PORT")
    )
    
if __name__ == "__main__":
    asyncio.run(main())