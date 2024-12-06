import dash
from dash import Dash, html, Input, Output, State, callback, dcc, ALL, Patch
from dash.exceptions import PreventUpdate
from backend import opcuaClient, mqttClient
import asyncio
import dash_daq as daq
import logging
from common import runtime_manager
from state.page_state_manager import PageStateManager

layout = html.Div(
    [
        html.Div([
            html.H2('Environmental Variables')
        ], className='environment'),
        html.Div([
            html.H2('Sorting Line Data'),
            html.Table([
                html.Tr([
                    html.Th(),
                    html.Th('Active', className='label'),
                    html.Th('Error', className='label'),
                    html.Th('Error message', className='label'),
                    html.Th('Workpiece ID', className='label'),
                    html.Th('Workpiece type', className='label'),
                    html.Th('On transport belt', className='label'),
                    html.Th('Color', className='label'),
                ]),
                html.Tr()
            ], className='device-data-table', id='sld-table'),
        ], className='sld'),
        dcc.Store(id='sld-history')
    ],
    className='factory-data'
)

@callback(
    Output('sld-table', 'children'),
    Input('updater', 'n_intervals'),
    State('sld-table', 'children')
)
def update_sld(n_intervals, el):    
    psm = PageStateManager()
    data = psm.get('factory-data', 'state_sld')
    
    if not data:
        raise PreventUpdate
    
    print('doing update!')
    patch = Patch() # patch object of the sld-table children.
    
    patch[1] = html.Tr([
            html.Td('Latest')
        ] + [ # patch[1] is the first <tr> element, the 0th is the headers
            html.Td(str(data.get(v, 'No data yet')), className='value') 
            for v in ['active', 'error', 'errorMessage', 'workpieceID', 'workpieceType', 'onTransportBelt', 'observedColor']
        ])

    return patch

dash.register_page(__name__, path='/factory-data', layout=layout)
