import dash
from dash import Dash, html, Input, Output, State, callback, dcc, no_update
from dash.exceptions import PreventUpdate
from dash_extensions import WebSocket
import asyncio
import logging
import dash_daq as daq
import os
from common import RuntimeManager
from asyncio import sleep
from pages.components import hbw_view, display_hbw
import json
from backend import MqttClient
import datetime
import asyncio
import base64
import cv2

layout = html.Div(
    [
        *[WebSocket(
            id={"source": "mqtt", "topic": topic},
            url=f"ws://10.35.4.254:8765/{topic}"
        ) for topic in [
            'f/setup', 
            'f/o/setup/reponse', 
            'Turtlebot/CurrentState', 
            'f/o/state/ack/response',
            'o/ptu/response',
            'fl/i/nfc/ds',
            'fl/o/nfc/ds'
        ]],
        
        html.Link(href="../assets/overview.css", rel="stylesheet"),
        html.Div(id="dummy"),
        html.Div(
            [
                html.Div([html.H2("Camera"), html.Img(id='camera-output')], className="camera"),
            ],
            className="camera-container",
        ),
        html.Div(
            [
                html.Div(device, className="device-status")
                for device in [
                    "PLC",
                    "TXT",
                    "Turtlebot",
                    "Fischer Extension",
                    "Cam",
                    "Raspi",
                ]
            ],
            className="component-status",
        ),
        html.Div(
            [
                html.H2("Camera Control"),
                html.Div(
                    [
                        html.Div(),
                        html.Button(
                            "🡡",
                            id="camera-upwards-button",
                            className="arrow-button button",
                        ),
                        html.Button(
                            "🞁", 
                            id="camera-up-button", 
                            className="arrow-button button"
                        ),
                        html.Div(),
                        html.Button(
                            "🡠",
                            id="camera-leftwards-button",
                            className="arrow-button button",
                        ),
                        html.Button(
                            "🞀",
                            id="camera-left-button",
                            className="arrow-button button",
                        ),
                        html.Button(
                            html.I(className="fas fa-home"),
                            id="camera-home-button",
                            className="button",
                        ),
                        html.Button(
                            "🞂",
                            id="camera-right-button",
                            className="arrow-button button",
                        ),
                        html.Button(
                            "🡢",
                            id="camera-rightwards-button",
                            className="arrow-button button",
                        ),
                        html.Button(
                            html.I(className="fas fa-stop"),
                            id="camera-stop-button",
                            className="button",
                        ),
                        html.Button(
                            "🡣",
                            id="camera-downwards-button",
                            className="arrow-button button",
                        ),
                        html.Button(
                            "🞃",
                            id="camera-down-button",
                            className="arrow-button button",
                        ),
                    ],
                    id="camera-control-button-menu",
                ),
            ],
            className="camera-control",
        ),
        hbw_view,
        html.Div(
            [
                html.H2("Factory Control"),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span("Version Index PLC", className="label"),
                                html.P(
                                    "Loading...", className="value", id="plc-version"
                                ),
                                html.Span("Version Index HMI", className="label"),
                                html.P("1.4", className="value"),
                            ],
                            className="factory-control-header table",
                        ),
                        html.Div(
                            [
                                html.H3("NFC Commands from PLC"),
                                html.Button("NFC READ", id='nfc-command-read'),
                                html.Button("NFC READ_UID", id='nfc-command-read-uid'),
                                html.Button("NFC WRITE", id='nfc-command-write'),
                                html.Button("NFC DELETE", id='nfc-command-delete'),
                            ],
                            className="nfc-control-button-menu",
                        ),
                        html.Div(
                            [
                                html.Span("Clear HBW Rack:", className="label"),
                                html.Button("CLEAR", id="clear-rack"),
                                html.Span(
                                    "Fill HBW Rack (during 60s after PLC startup):",
                                    className="label",
                                ),
                                html.Button("FILL"),
                                html.Span("Move to park position:", className="label"),
                                html.Button("PARKING"),
                                html.Span("Acknowledge Errors:", className="label"),
                                html.Button("ACK", id='acknowledge-errors'),
                                html.Span(
                                    "Restart OPCUA/MQTT interface:", className="label"
                                ),
                                html.Button("RESTART"),
                            ],
                            className="factory-control-button-menu table",
                        ),
                        html.H3("NFC Output"),
                        html.Div(
                            [
                                html.Button("No puck detected", id='nfc-detected-puck-id'),
                                html.Button("No colour detected", id='nfc-detected-puck-type')
                            ],
                            className="order-button-menu",
                        ),
                    ],
                    className="factory-control-container",
                ),
            ],
            className="factory-control",
        ),
        html.Div(
            [
                html.H2("Turtlebot Control"),
                html.Div(
                    [
                        html.Span("Version", className="label"),
                        html.P("0.0", className="value"),
                        html.Span("State Turtlebot", className="label"),
                        html.P("Loading...", className="value"),
                        dcc.Dropdown(
                            id="turtlebot-state-dropdown",
                            options=[
                                {"label": "Option 1", "value": "option1"},
                                {"label": "Option 2", "value": "option2"},
                                {"label": "Option 3", "value": "option3"},
                            ],
                            placeholder="Select an option",
                            className="dropdown",
                        ),
                        html.Span("Current State", className="label"),
                        html.P("Offline", className="value"),
                    ],
                    className="turtlebot-control-container table",
                ),
            ],
            className="turtlebot-control",
        ),
        html.Div(
            [
                html.H2("Extension Control"),
                html.Div(
                    [
                        html.Span("State", className="label"),
                        daq.ToggleSwitch(value=False),
                        html.Span("Speed", className="label"),
                        dcc.Input(
                            type="number",
                            value=0,
                            debounce=True,
                        ),
                        html.Span("Slagboom", className="label"),
                        daq.ToggleSwitch(value=False),
                        html.Span("Slatus container place 1", className="label"),
                        html.P("down", className="value"),
                        html.Span("Slatus container place 2", className="label"),
                        html.P("down", className="value"),
                    ],
                    className="extension-control-container, table",
                ),
            ],
            className="extension-control",
        ),
    ],
    className="overview",
)


@callback(
    Output("plc-version", "children"), 
    Input({"source": "mqtt", "topic": "f/setup"}, "message"))
def display_plc_version(setup):

    if setup is None:
        raise PreventUpdate

    setup = json.loads(setup.get('data'))
    return str(setup.get("versionSPS"))

@callback(
    [
        Output("clear-rack", "className"),
        Output("clear-rack", "disabled"),
        Output("clear-rack", "title")
    ],
    Input('clear-rack', 'n_clicks'),
    prevent_initial_call=True
)
def clear_rack(n_clicks):
    rtm = RuntimeManager()
    mqtt_client = MqttClient()
    rtm.add_task(mqtt_client.publish('f/o/setup', {
        'cleanRackHBW': True
    }))
    return (
        "pending",
        True,
        "Disabled: Pending",
    )

@callback(
    [
        Output("acknowledge-errors", "className", allow_duplicate=True),
        Output("acknowledge-errors", "disabled", allow_duplicate=True),
        Output("acknowledge-errors", "title", allow_duplicate=True)
    ],
    Input('acknowledge-errors', 'n_clicks'),
    prevent_initial_call=True
)
def acknowledgeErrors(n_clicks):
    rtm = RuntimeManager()
    mqtt_client = MqttClient()
    logging.info('Acknowledging errors...')
    
    now = datetime.datetime.now()
    rtm.add_task(mqtt_client.publish('f/o/state/ack', now))
    
    return ("pending",True,"Disabled: Pending")
    
@callback(
    [
        Output("acknowledge-errors", "className", allow_duplicate=True),
        Output("acknowledge-errors", "disabled", allow_duplicate=True),
        Output("acknowledge-errors", "title", allow_duplicate=True)
    ],
    Input({"source": "mqtt", "topic": "f/o/state/ack/response"}, "message"),
    prevent_initial_call=True
)
def resetAcknowledgeErrors(message):
    """Resets the acknowledge button when the relay sends a response.
    """
    message = json.loads(message.get('data'))

    if message.get('err'):
        logging.error(message.get('err'))
    else:
        logging.info(message.get('msg'))
    return ('label', False, '')
    
# PTU control
commands = {
    'up': ['relmove_up', 10],
    'right': ['relmove_right', 10],
    'left': ['relmove_left', 10],
    'down': ['relmove_down', 10],
    'downwards': ['start_tilt', 1],
    'upwards': ['end_tilt', 1],
    'leftwards': ['start_pan', 1],
    'rightwards': ['end_pan', 1],
    'home': ['home', 1],
    'stop': ['stop', 1]
}

def gen_ptu_control_callback(direction: str):
   
    @callback(
        Output(f'camera-{direction}-button', 'className', allow_duplicate=True),
        Output(f'camera-{direction}-button', 'disabled', allow_duplicate=True),
        Output(f'camera-{direction}-button', 'title', allow_duplicate=True),
        Input(f'camera-{direction}-button', "n_clicks"),
        prevent_initial_call=True
    )
    def ptu_control_callback(n_clicks, direction=direction):
        print(direction)
        mqttClient = MqttClient()
        rtm = RuntimeManager()
        rtm.add_task(
            mqttClient.publish(
                topic="o/ptu",
                payload={
                    'cmd': commands.get(direction)[0],
                    'degree': commands.get(direction)[1],
                    'ts': datetime.datetime.now()
                }
            )
        )
        logging.info(f'Sending PTU command for direction <{direction}> to PLC...')
        return ("pending",True,"Disabled: Pending")
    
    @callback(
        Output(f'camera-{direction}-button', 'className', allow_duplicate=True),
        Output(f'camera-{direction}-button', 'disabled', allow_duplicate=True),
        Output(f'camera-{direction}-button', 'title', allow_duplicate=True),
        Input({"source": "mqtt", "topic": "o/ptu/response"}, "message"),
        State(f'camera-{direction}-button', 'disabled'),
        prevent_initial_call=True
    )
    def reset_ptu_button(message, is_disabled, direction=direction):
        if not is_disabled:
            raise PreventUpdate
        
        message = json.loads(message.get('data'))
        if message.get('err'):
            logging.error(message.get('err'))
        else:
            logging.info(message.get('msg'))
        return ('button', False, '')
    
for direction in commands:
    gen_ptu_control_callback(direction)
    
# Camera image
@callback(
    Output('camera-output', 'src'),
    Input('updater', 'n_intervals')
)
def capture_image(n_intervals):
    """Captures an image periodically using the USB camera and displays it as a html.Img.
    """
    
    try:
        capture = cv2.VideoCapture(0)
        ret, frame = capture.read()
        capture.release()
        
        if not ret:
            raise PreventUpdate
        
        _, buffer = cv2.imencode('.jpg', frame)
        encoded_image = base64.b64encode(buffer).decode('utf-8')
        return f'data:image/jpeg;base64,{encoded_image}'
    except Exception as e:
        logging.warning(f'Error while trying to capture camera image: {e} ({type(e)})')
    
# NFC Reader
    
@callback(
    [
        Output('nfc-command-read', 'style'),
        Output('nfc-command-read-uid', 'style'),
        Output('nfc-command-write', 'style'),
        Output('nfc-command-delete', 'style')
    ],
    Input({"source": "mqtt", "topic": "fl/o/nfc/ds"}, "message")
)
def display_nfc_commands(command):
    if command is None:
       raise PreventUpdate 
    command = json.loads(command.get('data'))['cmd']
    
    off = {"background-color": "gray"}
    on = {"background-color": "#0094CE"}
    
    return (
        on if command == 'read' else off,
        on if command == 'read_uid' else off,
        on if command == 'write' else off,
        on if command == 'delete' else off,
    )
    
@callback(
    [
        Output('nfc-detected-puck-id', 'children'),
        Output('nfc-detected-puck-type', 'children')
    ],
    Input({"source": "mqtt", "topic": "fl/i/nfc/ds"}, "message")
)
def display_nfc_output(detected_puck):
    if detected_puck is None:
        raise PreventUpdate
    detected_puck = json.loads(detected_puck.get('data')).get('workpiece')
    
    return (
        detected_puck['id'] if (detected_puck is not None) else 'No puck ID detected', 
        detected_puck['type'] if (detected_puck is not None) else 'No puck colour detected'
    )
    
display_hbw    

dash.register_page(
    __name__, path="/", redirect_from=["/factory-overview"], layout=layout
)
