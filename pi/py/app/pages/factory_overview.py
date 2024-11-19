import dash
from dash import Dash, html, Input, Output, State, callback, dcc, no_update
from dash.exceptions import PreventUpdate
from dash_extensions import WebSocket
from backend import mqttClient, opcuaClient
from common import runtime_manager
from page_state_manager import PageStateManager
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
                    dcc.Input(type='number', value=0, debounce=True,),
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

@callback(Output('plc-version', 'children'), Input('updater', 'n_intervals'))
def display_plc_version(n_intervals):
    psm = PageStateManager()
    data = psm.get_data('factory-overview', 'plc_version')
    
    if not data:
        print("display called with None")
        raise PreventUpdate
    else:
        print("updating layout with version: " + str(data))
        return str(data)
    

dash.register_page(__name__, path='/', redirect_from=['/factory-overview'], layout=layout)