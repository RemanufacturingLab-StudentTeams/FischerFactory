import pprint
from dash import dcc, html, Input, Output, Dash
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
from threading import Thread

async def init_dash() -> Dash:
    app = Dash(__name__,
            external_stylesheets=[
                "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"
            ],
            external_scripts=[
                "https://cdn.socket.io/4.0.0/socket.io.min.js"
            ],
            use_pages=True,
            prevent_initial_callbacks=True
            )
    
    from global_layout import layout
    app.layout = await layout()
    
    @app.callback(
        [Output("mqtt-broker-status", "children"), Output("mqtt-broker-status", "style")],
        Input("updater", "n_intervals"),
    )
    def update_status_mqtt(n_intervals):
        client = mqttClient.MqttClient()
        status_text = f"MQTT Broker at {os.getenv('MQTT_BROKER_IP')}: "

        if client.get_status():
            status_text += "OK"
            style = {
                "backgroundColor": "green",
                "color": "white",
            }
        elif client.get_reconnection_attempts() < 10:
            status_text += (
                f"Reconnecting... {client.get_reconnection_attempts()}/10 attempts"
            )
            style = {
                "backgroundColor": "yellow",
                "color": "black",
            }
        else:
            status_text += "Disconnected"
            style = {
                "backgroundColor": "red",
                "color": "white",
            }

        return status_text, style

    @app.callback(
        [Output("dummy", "children", allow_duplicate=True)], 
        Input("location", "href")
    )
    def switch_page(href: str):
        import logging # bit weird to not put this import at the top of the page but the logger setup really needs to run first so ¯\_(ツ)_/¯
        # page_name = pathname.lstrip('/') or 'factory-overview'
        page_name = href.split('/')[-1].split('?')[0] or 'factory-overview'
        
        logging.debug(f"Switched to page: {page_name}")
        
        psm = PageStateManager()
        rtm  = runtime_manager.RuntimeManager()
        
        async def task():
            await psm.hydrate_page(page_name)
            await psm.monitor_page(page_name)
            
        rtm.add_task(task())
        
        return ['']
    
    return app

connected_clients = set() # ew, global variables

async def start_ws() -> WebSocketServer:
    import os # Cannot put this on the top of the file because it needs to be imported after the main function loads the environment variables
    import logging # same here, it needs to be set up first 
    
    async def websocket_handler(websocket):
        """Handles WebSocket connections and messages."""
        # Register the new client
        connected_clients.add(websocket)
        logging.info('[WS_SERVER] Client connected')
        try:
            async for message in websocket:
                logging.debug(f"[WS_SERVER] Received: {message}")
        except websockets.exceptions.ConnectionClosed:
            logging.info("[WS_SERVER] Client disconnected")
        finally:
            # Unregister the client
            connected_clients.remove(websocket)
        
    async def run_server() -> WebSocketServer:
        logging.info(f"Starting WebSocket server on ws://localhost:{os.getenv('WS_PORT')}...")
        ws_server = await websockets.serve(websocket_handler, "localhost", 8765)
        logging.info("WebSocket server is running.")
        return ws_server

    return (await run_server())

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
    ws_server = await start_ws()
    thread = Thread(target=ws_server.serve_forever, daemon=True)
    thread.start()
    
    # Init the Dash app
    app = await init_dash()
    
    # Register pages
    from pages.factory_overview import register as register_overview
    await register_overview()
    
    # Launch the app
    app.run(
        dev_tools_hot_reload=(config.mode == 'dev'), 
        debug=False, port=os.getenv("PORT")
    )
    
if __name__ == "__main__":
    asyncio.run(main())