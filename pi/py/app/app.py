import pprint
from dash import dcc, html, Dash, Input, Output
import dash
from dash import dcc
import logger
from dotenv import load_dotenv
import os, argparse
from backend import mqttClient, opcuaClient
from threading import Thread
from common import runtime_manager
from state import PageStateManager
from common import config

page_icons = {
    "Factory overview": "fas fa-home",
    "Factory data": "fas fa-bar-chart",
    "Dashboard customer": "fas fa-solid fa-cart-shopping",
    "Debug": "fa fa-bug",
}
# Global layout for the app
config.app.layout = html.Div(
    [
        dcc.Location('location'),
        html.Div(
            [
                html.Div("FischerFactory Dash Dashboard"),
                html.Div(
                    [
                        html.Div(
                            [], id="mqtt-broker-status", className="connection-status"
                        ),
                        html.Div(
                            [], id="opcua-plc-status", className="connection-status"
                        ),
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
                        dcc.Link(f"{page['name']}", href=(page["relative_path"])),
                    ],
                    className="side-panel-link",
                )
                for page in dash.page_registry.values()
                if page["module"] != "pages.not_found_404"
            ],
            className="side-panel",
        ),
        html.Div(id="feedback-div"),
        html.Div([], id="dummy"),
        html.Div(
            [
                dash.page_container,
            ],
            className="page-content",
        ),
        dcc.Interval(id="updater", n_intervals=0, interval=0.5 * 1000),
    ],
    className="wrapper",
)

layoutDebug = html.Div(
    [
        html.Button("debug", id="debug-button", n_clicks=0),
        html.Div(children="no clicks", id="debug-div"),
    ]
)


@config.app.callback(
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

@config.app.callback(
    [Output("dummy", "children", allow_duplicate=True)], 
    Input("location", "pathname")
)
def switch_page(pathname: str):
    import logging # bit weird to not put this import at the top of the page but the logger setup really needs to run first so ¯\_(ツ)_/¯
    page_name = pathname.lstrip('/') or 'factory-overview'
    
    logging.debug(f"Switched to page: {page_name}")
    
    psm = PageStateManager()
    rtm  = runtime_manager.RuntimeManager()
    
    rtm.add_task(psm.hydrate_page(page_name))
    rtm.add_task(psm.monitor_page(page_name))
    
    return ['']

@config.app.callback(
    [Output("opcua-plc-status", "children"), Output("opcua-plc-status", "style")],
    Input("updater", "n_intervals"),
)
def update_status_opcua(n_intervals):
    client = opcuaClient.OPCUAClient()
    status_text = f"PLC at {os.getenv('PLC_IP')}: " if config.mode == 'prod' else 'Mock PLC: '

    if client.get_status():
        status_text += 'OK'
        style = {'backgroundColor': 'green', 'color': 'white'}
    elif client.get_reconnection_attempts() < 10:
        status_text += f"Reconnecting... {client.get_reconnection_attempts()}/10 attempts"
        style = {'backgroundColor': 'yellow', 'color': 'black'}
    else:
        status_text += 'Disconnected'
        style = {'backgroundColor': 'red', 'color': 'white'}

    return status_text, style


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the application.")
    parser.add_argument("--dev", action="store_true", help="Run in development mode")
    config.mode = 'dev' if parser.parse_args().dev else 'prod'
    os.environ.clear()

    load_dotenv(dotenv_path=f".env.{config.mode}")
    print(
        f"Running in \033[0;33m{config.mode} mode\033[0m with environment variables:"
    )
    pprint.pprint(os.environ.copy())

    logger.setup()

    async def startClients():
        # Initialize the MQTT client
        mqtt = mqttClient.MqttClient()
        opcua = opcuaClient.OPCUAClient()

    # Start OPCUA and MQTT Clients (important: *before* starting the app!)
    rtm = runtime_manager.RuntimeManager()
    rtm.add_task(startClients())

    # Launch the Dash app
    config.app.run(
        dev_tools_hot_reload=(config.mode == 'dev'), 
        debug=False, port=os.getenv("PORT")
    )
