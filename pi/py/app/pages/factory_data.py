import dash
from dash import Dash, html, Input, Output, State, callback, dcc, ALL, Patch
from dash.exceptions import PreventUpdate
from dash_extensions import WebSocket
import asyncio
import dash_daq as daq
import logging
from common import runtime_manager, format_time_string
import json

layout = html.Div([
        *[WebSocket(
            id={"source": "mqtt", "topic": topic},
            url=f"ws://localhost:8765/{topic}"
        ) for topic in [
            'f/i/state/dsi',
            'f/i/state/dso',
            'f/i/state/mpo',
            'f/i/state/sld',
            'f/i/state/vgr',
            'f/i/state/hbw'
        ]],
        
        html.Link(href="../assets/data.css", rel="stylesheet"),

        html.Div([
            html.H2('Input Station Data'),
            html.Table(className='station-data-table', id='dsi-table'), # children dynamically generated via callback
        ], className='dsi'),
        
        html.Div([
            html.H2('Output Station Data'),
            html.Table(className='station-data-table', id='dso-table'), # children dynamically generated via callback
        ], className='dso'),

        html.Div([
            html.H2('Multi Processing Station Data'),
            html.Table(className='station-data-table', id='mpo-table'), # children dynamically generated via callback
        ], className='mpo'),
            
        html.Div([
            html.H2('Sorting Line Data'),
            html.Table(className='station-data-table', id='sld-table'), # children dynamically generated via callback
        ], className='sld'),
        
        html.Div([
            html.H2('Vacuum Gripper Data'),
            html.Table(className='station-data-table', id='vgr-table'), # children dynamically generated via callback
        ], className='vgr'),
        
        html.Div([
            html.H2('High Bay Warehouse Data'),
            html.Table(className='station-data-table', id='hbw-table'), # children dynamically generated via callback
        ], className='hbw')
    ],
    className='factory-data'
)

def gen_callback(station: str):
    @callback(
        Output(f'{station}-table', 'children'),
        Input({'source': 'mqtt', 'topic': f'f/i/state/{station}'}, 'message')
    )
    def display(state_in):      
        if state_in is None:
            raise PreventUpdate
            
        state_in = json.loads(state_in.get('data'))
        
        if state_in.get('error'):
            logging.error(f'Error on {station.upper()}: {state_in.get('errorMessage')}')
            
        return [
            html.Tr([
                html.Th('Active', className='label'),
                html.Th('Error', className='label'),
                html.Th('Error message', className='label'),
                html.Th('Workpiece ID', className='label'),
                html.Th('Workpiece Colour', className='label'),
                html.Th('Workpiece State', className='label'),
                html.Th('Local Time', className='label')
            ]),
            html.Tr([
                html.Td(state_in.get('active') or 'No'),
                html.Td(state_in.get('error') or 'No error'),
                html.Td(state_in.get('errorMessage') or ''),
                html.Td(state_in.get('workpiece').get('id') if state_in.get('workpiece').get('id') != '0' else 'No workpiece'),
                html.Td(state_in.get('workpiece').get('type') or ''),
                html.Td(state_in.get('workpiece').get('state')),
                html.Td(format_time_string(state_in.get('ts')))
            ])
        ]

gen_callback('dsi')
gen_callback('dso')
gen_callback('mpo')        
gen_callback('sld')
gen_callback('vgr')
gen_callback('hbw')

dash.register_page(__name__, path='/factory-data', layout=layout)
