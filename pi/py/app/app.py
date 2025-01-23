import pprint
from dash import dcc, html, Input, Output, Dash, ALL, callback, State
from dash_extensions import WebSocket as FrontEndWebSocket
import logger
from dotenv import load_dotenv
import os, argparse
from backend import mqttClient
from threading import Thread
from common import RuntimeManager
from common import config
import asyncio
import websockets
from websockets.asyncio.server import Server as WebSocketServer
from websockets.asyncio.server import ServerConnection
from websockets.http11 import Request
from websockets import Origin
from threading import Thread
import json
import flask_cors
from datetime import date, datetime
from logger import frontend_log

def init_dash() -> Dash:
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
    
    server = app.server
    flask_cors.CORS(server)
    
    from dash import page_registry, page_container
    from backend import MqttClient
    from common import RuntimeManager
    import os

    # Global layout for the app
    page_icons = {
        "Factory overview": "fas fa-home",
        "Factory data": "fas fa-bar-chart",
        "Dashboard customer": "fas fa-solid fa-cart-shopping",
        "Debug": "fa fa-bug",
    }
    
    layout = html.Div(
        [
            *[FrontEndWebSocket(
                id={"source": "mqtt", "topic": topic},
                url=f"ws://localhost:8765/{topic}" # I would LOVE to add a `os.getenv` in here, but if I do that for some reason it stops working. Thanks Plotly Dash.
            ) for topic in ['relay/f/i/stock']],
            dcc.Location("location", refresh=True),
            html.Div(
                [
                    html.Div("FischerFactory Dash Dashboard"),
                    html.Div(
                        [
                            html.Div(
                                [], id="mqtt-broker-status", className="connection-status"
                            )
                        ],
                        className="status-container",
                    ),
                ],
                id="banner-title",
                className="banner title",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.I(
                                className=page_icons[page["name"]], style={"margin": "5px"}
                            ),
                            dcc.Link(
                                f"{page['name']}",
                                href=(page["relative_path"]),
                                refresh=True,
                            ),
                        ],
                        className="side-panel-link",
                    )
                    for page in page_registry.values()
                    if page["module"] != "pages.not_found_404"
                ] + [
                    html.Div(
                        [
                            html.H2('Log'),
                            html.Div(id='log-output')
                        ],
                        className='log-output'
                    ),
                    html.Div(id='log')
                ],
                className="side-panel",
            ),
            html.Div(id="feedback-div"),
            html.Div([], id="dummy"),
            html.Div(
                [
                    page_container,
                ],
                className="page-content",
            ),
            dcc.Interval(
                id="updater", n_intervals=0, interval=2 * 1000
            ),  # 2 second interval
        ],
        className="wrapper",
    )


    @callback(
        [Output("mqtt-broker-status", "children"), Output("mqtt-broker-status", "style")],
        Input("updater", "n_intervals"),
    )
    def update_status_mqtt(n_intervals):
        client = MqttClient()
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


    @callback(
        Output(component_id={"source": "mqtt", "topic": ALL}, component_property="send"),
        Input("location", "href"),
        State(component_id={"source": "mqtt", "topic": ALL}, component_property="id")
    )
    def switch_page(href: str, websockets: list[str]):
        import logging  # bit weird to not put this import at the top of the page but the logger setup really needs to run first so ¯\_(ツ)_/¯

        # page_name = pathname.lstrip('/') or 'factory-overview'
        page_name = href.split("/")[-1].split("?")[0] or "factory-overview"

        logging.debug(f"Switched to page: {page_name}")

        return ["keepalive" for w in websockets]  # send keepalive signal over WebSockets

    @callback(
        Output('log-output', 'children'),
        Input('updater', 'n_intervals')
    )
    def display_log(n_intervals):
        log = list(frontend_log)
        return log or html.Tr('<empty>')

    app.layout = layout    
    
    return app

connections: dict[str, ServerConnection] = {} # global variables, ew

def start_ws():
    import os # Cannot put this on the top of the file because it needs to be imported after the main function loads the environment variables
    import logging # same here, it needs to be set up first 
    from backend import MqttClient
    
    async def connection_handler(conn: ServerConnection):
        """Handles WebSocket connections and messages."""
        try:
            async for message in conn:
                logging.debug(f"[WS_SERVER] Received: {message}")
        except websockets.ConnectionClosed | websockets.ConnectionClosedError | websockets.ConnectionClosedOK:
            logging.debug(f'[WS_SERVER] Client disconnected')
            topic = [k for k, v in connections if v == conn][0]
            mqttClient = MqttClient()
            mqttClient.client.unsubscribe(topic)
            connections.pop(topic)
    
    def request_handler(conn: ServerConnection, req: Request):
        topic = req.path.lstrip('/')
        logging.debug(f'[WS_SERVER] Adding ServerConnection for {topic}')
        connections[topic] = conn
        
        rtm = RuntimeManager()
        mqttClient = MqttClient()
        
        if topic.startswith('relay'):
            # hydrate
            rtm.add_task( 
                mqttClient.publish(
                    os.getenv("MQTT_RELAY_TOPIC") + "/read",
                    {
                        "topics": [topic]
                    }
                )
            )
        
        async def cb(msg: dict, conn=conn, topic=topic):
            logging.debug(f'[WS_SERVER] Received message on {topic}')
            if msg.get('ts'): # Filter out midnight times, which the PLC ues as a default when it has no time data sometimes
                t = None
                try:
                    t = datetime.strptime(msg['ts'], '%Y-%m-%dT%H:%M:%S.%f%z').time()
                except Exception:
                    t = datetime.strptime(msg['ts'], '%Y-%m-%dT%H:%M:%S%z').time()
                if (t.hour == 0) and (t.minute == 0) and (t.second == 0):
                    msg['ts'] = ''
            try:
                await conn.send(json.dumps(msg))
                logging.debug(f'[WS_SERVER] Data from {topic} sent to frontend.')
            except Exception as e:
                logging.error(f"[WS_SERVER] Failed to send message to frontend WebSocket {topic}: {e}")
        rtm.add_task(
            mqttClient.subscribe(
                topic,
                callback=cb
            )
        )
    
    async def run_server():
        logging.info(f"Starting WebSocket server on ws://localhost:{os.getenv('WS_PORT')}...")
        async with websockets.serve(
            handler=connection_handler, 
            host="localhost", 
            port=8765, 
            process_request=request_handler
        ):
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
    
    # Init the Dash app
    app = init_dash()
    
    # Launch the app
    app.run(
        dev_tools_hot_reload=(config.mode == 'dev'), 
        debug=False, port=os.getenv("PORT")
    )
    
if __name__ == "__main__":
    asyncio.run(main())