import dash
from dash import Dash, html, Input, Output, State, callback, dcc, ALL, Patch
from dash.exceptions import PreventUpdate
from dash_extensions import WebSocket
import asyncio
import dash_daq as daq
import logging
from common import runtime_manager
import json

layout = html.Div([
        *[WebSocket(
            id={"source": "mqtt", "topic": topic},
            url=f"ws://localhost:8765/{topic}"
        ) for topic in [
            'relay/f/i/state/sld'
        ]],
            
        html.Div([
            html.H2('Sorting Line Data'),
            html.Table(className='device-data-table', id='sld-table'), # children dynamically generated via callback
        ], className='sld')
    ],
    className='factory-data'
)

@callback(
    Output('sld-table', 'children'),
    Input({'source': 'mqtt', 'topic': 'relay/f/i/state/sld'}, 'message')
)
def display_sld(state_sld):      
    if state_sld is None:
        raise PreventUpdate
          
    state_sld = json.loads(state_sld.get('data'))
    print(state_sld)
          
    return [
        html.Tr([
            html.Th('Active', className='label'),
            html.Th('Error', className='label'),
            html.Th('Error message', className='label'),
            html.Th('Workpiece ID', className='label'),
            html.Th('Workpiece Colour', className='label'),
            html.Th('Workpiece State', className='label')
        ]),
        html.Tr([
            html.Td(state_sld.get('active') or 'No'),
            html.Td(state_sld.get('error') or 'No error'),
            html.Td(state_sld.get('errorMessage') or ''),
            html.Td(state_sld.get('workpiece').get('id') if state_sld.get('workpiece').get('id') != '0' else 'No workpiece'),
            html.Td(state_sld.get('workpiece').get('type') or ''),
            html.Td(state_sld.get('workpiece').get('state'))
        ])
    ]

dash.register_page(__name__, path='/factory-data', layout=layout)
