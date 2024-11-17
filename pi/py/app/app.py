import pprint
from dash import dcc, html, Dash, Input, Output
import dash
import logger
from dotenv import load_dotenv
import page_icons
import os, argparse
from backend import mqttClient, opcuaClient
import asyncio
from threading import Thread
from common import runtime_manager, server

# Global layout for the app
server.app.layout = html.Div(
    [
        html.Div([
                    html.Div('FischerFactory Dash Dashboard'),
                    html.Div([
                        html.Div([], id='mqtt-broker-status', className='connection-status'),
                        html.Div([], id='opcua-plc-status', className='connection-status')
                    ], className='status-container')
                ],
            id='banner-title',
            className='banner title'
            ),
        html.Div(
            [
                html.Div([
                    html.I(className=page_icons.i[page['name']], style={"margin": "5px"}),
                    dcc.Link(
                        f"{page['name']}", href=(page["relative_path"])
                    )
                    ],
                    className='side-panel-link'
                )
                for page in dash.page_registry.values()
                if page["module"] != "pages.not_found_404"
            ],
            className='side-panel',
        ),
        html.Div(
            id='feedback-div'
        ),
        html.Div([
            dash.page_container,
            ],
            className='page-content'   
        ),
        dcc.Interval(id='updater', n_intervals=0, interval=0.5 * 1000) 
    ],
    className='wrapper'
)

layoutDebug = html.Div([
    html.Button('debug', id='debug-button', n_clicks=0),
    html.Div(children='no clicks', id='debug-div')
])

@server.app.callback(
    [Output('mqtt-broker-status', 'children'), Output('mqtt-broker-status', 'style')],
    Input('updater', 'n_intervals')
)
def update_status_mqtt(n_intervals):
    client = mqttClient.MqttClient()
    status_text = f"MQTT Broker at {os.getenv('MQTT_BROKER_IP')}: "
    
    if client.get_status():
        status_text += 'OK'
        style = {'backgroundColor': 'green', 'color': 'white', 'padding': '10px', 'borderRadius': '5px', 'margin': '5px', 'fontSize': '60%'}
    elif client.get_reconnection_attempts() < 10:
        status_text += f"Reconnecting... {client.get_reconnection_attempts()}/10 attempts"
        style = {'backgroundColor': 'yellow', 'color': 'black', 'padding': '10px', 'borderRadius': '5px', 'margin': '5px', 'fontSize': '60%'}
    else:
        status_text += 'Disconnected'
        style = {'backgroundColor': 'red', 'color': 'white', 'padding': '10px', 'borderRadius': '5px', 'margin': '5px', 'fontSize': '60%'}
    
    return status_text, style

@server.app.callback(
    [Output('opcua-plc-status', 'children'), Output('opcua-plc-status', 'style')],
    Input('updater', 'n_intervals')
)
def update_status_opcua(n_intervals):
    # client = opcuaClient.OPCUAClient()
    status_text = f"PLC at {os.getenv('PLC_IP')}: "
    
    # if client.get_status():
    #     status_text += 'OK'
    #     style = {'backgroundColor': 'green', 'color': 'white', 'padding': '10px', 'borderRadius': '5px', 'margin': '5px', 'fontSize': '60%'}
    # elif client.get_reconnection_attempts() < 10:
    #     status_text += f"Reconnecting... {client.get_reconnection_attempts()}/10 attempts"
    #     style = {'backgroundColor': 'yellow', 'color': 'black', 'padding': '10px', 'borderRadius': '5px', 'margin': '5px', 'fontSize': '60%'}
    # else:
    #     status_text += 'Disconnected'
    #     style = {'backgroundColor': 'red', 'color': 'white', 'padding': '10px', 'borderRadius': '5px', 'margin': '5px', 'fontSize': '60%'}
    
    status_text += 'OK'
    style = {'backgroundColor': 'green', 'color': 'white', 'padding': '10px', 'borderRadius': '5px', 'margin': '5px', 'fontSize': '60%'}
    
    return status_text, style

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the application.')
    parser.add_argument('--dev', action='store_true', help='Run in development mode')
    dev = parser.parse_args().dev
    os.environ.clear()
    
    load_dotenv(dotenv_path=('.env-dev' if dev else '.env-prod'))
    print(f"Running in \033[0;33m{'development' if dev else 'production'} mode\033[0m with environment variables:")
    pprint.pprint(os.environ.copy())
    
    logger.setup()
    
    async def startClients():
        # Initialize the MQTT client
        mqtt = mqttClient.MqttClient()
        # opcua = opcuaClient.OPCUAClient()
    
    # Start OPCUA and MQTT Clients (important: *before* starting the app!)
    rtm = runtime_manager.RuntimeManager()
    rtm.add_task(startClients())
    
    # Launch the Dash app (by running SocketIO, automatically starting Dash as well)
    server.socketio.run(server.server, host='127.0.0.1', port=os.getenv('PORT'))
    