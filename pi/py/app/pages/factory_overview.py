import dash
from dash import Dash, html, Input, Output, State, callback, dcc, no_update
from dash.exceptions import PreventUpdate
from dash_extensions import WebSocket
from backend import mqttClient, opcuaClient
from common import runtime_manager
import asyncio
import logging
import dash_daq as daq
import os
from common import runtime_manager
from asyncio import sleep

layout = html.Div(
    [
        html.Link(href='../assets/overview.css', rel='stylesheet'),
        dcc.Store(id={'type': 'store'}, storage_type='local'),
        html.Div(id='dummy'),
        html.Div([
            html.Div([
                html.H2('Camera'),
                html.Img()
            ], className='camera'),
            
        ], className='camera-container'),
        
        html.Div([html.Div(device, className='device-status') for device in 
                ['PLC', 'TXT', 'Turtlebot', 'Fischer Extension', 'Cam', 'Raspi']
            ], className='component-status'
        ),
                
        html.Div(
            [
                html.H2('Camera Control'),
                html.Div([               
                    html.Div(),     
                    html.Button("🡡", id="camera-upwards-button", className="arrow-button button"),
                    html.Button("🞁", id="camera-up-button", className="arrow-button button"),
                    html.Div(),   
                    html.Button("🡠", id="camera-leftwards-button", className="arrow-button button"),
                    html.Button("🞀", id="camera-left-button", className="arrow-button button"),
                    html.Button(html.I(className='fas fa-home'), id="camera-home-button", className="button"),
                    html.Button("🞂", id="camera-left-button", className="arrow-button button"),
                    html.Button("🡢", id="camera-leftwards-button", className="arrow-button button"),
                    html.Button(html.I(className='fas fa-stop'), id="camera-stop-button", className="button"),
                    html.Button("🡣", id="camera-downwards-button", className="arrow-button button"),
                    html.Button("🞃", id="camera-down-button", className="arrow-button button")
                ], id='camera-control-button-menu')
            ],
            className='camera-control'
        ),
        
        html.Div(
            [
                html.H2('HBW View'),
                html.Div([
                    html.Div(),
                    html.Span('1', className='label'),
                    html.Span('2', className='label'),
                    html.Span('3', className='label'),
                    html.Span('A', className='label'),
                    html.Button(),
                    html.Button(),
                    html.Button(),
                    html.Span('B', className='label'),
                    html.Button(),
                    html.Button(),
                    html.Button(),
                    html.Span('C', className='label'),
                    html.Button(),
                    html.Button(),
                    html.Button(),
                ], className='hbw-view-container button-menu')
            ],
            className='hbw-view'
        ),
                
        html.Div(
            [
                html.H2('Factory Control'),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span('Version Index PLC', className='label'),
                                html.P('Loading...', className='value', id='plc-version'),
                                html.Span('Version Index HMI', className='label'),
                                html.P('1.4', className='value')
                            ], className='factory-control-header table'
                        ),    
                        html.Div([
                            html.H3('NFC Control'),
                            html.Button('NFC READ'),
                            html.Button('NFC READ_UID'),
                            html.Button('ACK'),
                            html.Button('NFC DELETE')
                            ], className='nfc-control-button-menu'),
                        html.Div([
                            html.Span('Clear HBW Rack:', className='label'),
                            html.Button('CLEAR', id='clear-button'),
                            html.Span('Fill HBW Rack (during 60s after PLC startup):', className='label'),
                            html.Button('FILL'),
                            html.Span('Move to park position:', className='label'),
                            html.Button('PARKING'),
                            html.Span('Acknowledge Errors:', className='label'),
                            html.Button('ACK'),
                            html.Span('Restart OPCUA/MQTT interface:', className='label'),
                            html.Button('RESTART')
                        ], className='factory-control-button-menu table'),
                        html.H3('Order'),
                        html.Div([
                            html.Button('WHITE'),
                            html.Button('BLUE'),
                            html.Button('RED')
                            ], className='order-button-menu')
                    ],
                    className='factory-control-container'  
                ),
            ],
            className='factory-control'
        ),
        
        html.Div([
            html.H2('Turtlebot Control'),
            html.Div(
                [
                    html.Span('Version', className='label'),
                    html.P('0.0', className='value'),
                    html.Span('State Turtlebot', className='label'),
                    html.P('Loading...', className='value'),
                    dcc.Dropdown(
                        id='turtlebot-state-dropdown',
                        options=[
                            {'label': 'Option 1', 'value': 'option1'},
                            {'label': 'Option 2', 'value': 'option2'},
                            {'label': 'Option 3', 'value': 'option3'},
                        ],
                        placeholder='Select an option',
                        className='dropdown'
                    ),
                    html.Span('Current State', className='label'),
                    html.P('Offline', className='value'),
                ], 
                className='turtlebot-control-container table'
            )], className='turtlebot-control'
        ),
        
        
        html.Div(
            [
                html.H2('Extension Control'),
                html.Div([
                    html.Span('State', className='label'),
                    daq.ToggleSwitch(value=False),
                    html.Span('Speed', className='label'),
                    dcc.Input(type='number', value=0),
                    html.Span('Slagboom', className='label'),
                    daq.ToggleSwitch(value=False),
                    html.Span('Slatus container place 1', className='label'),
                    html.P('down', className='value'),
                    html.Span('Slatus container place 2', className='label'),
                    html.P('down', className='value')
                ], className='extension-control-container, table')
            ], 
            className='extension-control')
    ],
    className='overview',
)

# Hydration: These values are filled in once, on page load    
@callback(Output('websocket-container', 'children'), Input('dummy', 'children'))
def hydrate(children):
    # opcua = opcuaClient.OPCUAClient()
    rtm = runtime_manager.RuntimeManager()
        
    async def mock_plc_call() -> float:
        logging.debug('hi?')
        await sleep(1.0)
        return 1.1
    
    # rtm.add_task(
    #     opcua.read('ns=3;s=\"gtyp_Setup\".\"r_Version_SPS\"'), 
    #     ws_endpoint='plc-version'
    # )
    
    rtm.add_task(
        mock_plc_call(),
        ws_endpoint='plc-version'
    )
    
    return [WebSocket(id='ws', url=f"ws://127.0.0.1:{os.getenv('PORT')}/plc-version")]

@callback(Output('plc-version', 'children'), Input('ws', 'message'))
def display_plc_version(data):
    logging.debug('Display called')
    if not data:
        print("display called with None")
        raise PreventUpdate
    else:
        print("updating layout with version: " + str(data))
        return str(data)

dash.register_page(__name__, path='/', redirect_from=['/overview'], layout=layout)

# Websocket idea: hydration function outputs Websocket components with endpoints to the layout, pass an emitter function to the callback in rtm, and then another callback inputs from ws and outputs to the layout

# Hydration: These values are filled in once, on page load    
@callback(
    Output('store', 'data'), 
    Input('updater', 'n_intervals'))
def hydrate(children):
    # opcua = opcuaClient.OPCUAClient()
    # opcua.read('ns=3;s=\"gtyp_Setup\".\"r_Version_SPS\"')
    
    async def mock_plc_version(value) -> float:
        await asyncio.sleep(1)
        return 1.1
    
    rtm = runtime_manager.RuntimeManager()
    logging.debug('hydrate!')
    rtm.add_task(
        mock_plc_version(''),
        ws_endpoint='plc-version'
    )
    
    return ''

@callback(Output('plc-version', 'children'), Input("updater", "n_intervals"))
def display_plc_version(message):
    logging.debug(message)
    
    if message is None:
        raise PreventUpdate
    else:
        logging.debug("called with some")
        return 'heh2'
