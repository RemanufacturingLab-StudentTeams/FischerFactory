import dash
from dash import Dash, html, Input, Output, State, callback, dcc, ALL, Patch
import dash_daq as daq
from backend import opcuaClient, mqttClient
import logging

layout = html.Div([
    html.Div([
        html.H2('ORder Configuration'),
        html.Div([
            html.Label('Colour picker'), # Bri'ish colour
            dcc.Dropdown(options=['Red','White','Blue'])
        ]),
        html.Div([
            html.Label('Baking'),
            daq.ToggleSwitch(value=False)
        ]),
        html.Div([
            html.Label('Baking time [ms]'),
            dcc.Input(type='number', value=4000, debounce=True, step=100)
        ]),
        html.Div([
            html.Label('Milling'),
            daq.ToggleSwitch(value=False)
        ]),
        html.Div([
            html.Label('Milling time [ms]'),
            dcc.Input(type='number', value=4000, debounce=True, step=100)
        ]),
        html.Button('ORDER')
    ], className='order-config'),
    html.Div([
        
    ], id='order-queue'),
    html.Div([
        html.Table([
            html.Tr([
                html.Th('Nr.'),
                html.Th('Colour'), # bo'el o' wo'uh
                html.Th('Oven'),
                html.Th('Milling')
            ])
        ])
    ], id='dashboard-customer-hbw')
], className='dashboard-customer')

dash.register_page(__name__, path='/dashboard-customer', layout=layout)