import dash
from dash import Dash, html, Input, Output, State, callback, dcc, ALL, Patch
from dash.exceptions import PreventUpdate
from backend import opcuaClient, mqttClient
import asyncio
import dash_daq as daq
import logging

layout = html.Div(
    [
        html.Div([
            html.H2('Environmental Variables')
        ], className='environment'),
        html.Div([
            html.H2('Sorting Line Data'),
            html.Table([
                html.Tr([
                    html.Th('Active', className='label'),
                    html.Th('Error', className='label'),
                    html.Th('Error message', className='label'),
                    html.Th('Workpiece ID', className='label'),
                    html.Th('Workpiece type', className='label'),
                    html.Th('On transport belt', className='label'),
                    html.Th('Color', className='label'),
                ]),
                html.Tr([
                    html.Td('No data yet', className='value', id={'type':'synced', 'topic': 'f/i/state/sld', 'field': 'active', 'index':0}), 
                    html.Td('No data yet', className='value', id={'type':'synced', 'topic': 'f/i/state/sld', 'field': 'error', 'index':0}),
                    html.Td('No data yet', className='value', id={'type':'synced', 'topic': 'f/i/state/sld', 'field': 'errorMessage', 'index':0}),
                    html.Td('No data yet', className='value', id={'type':'synced', 'topic': 'f/i/state/sld', 'field': 'workpieceID', 'index':0}),
                    html.Td('No data yet', className='value', id={'type':'synced', 'topic': 'f/i/state/sld', 'field': 'workpieceType', 'index':0}),
                    html.Td('No data yet', className='value', id={'type':'synced', 'topic': 'f/i/state/sld', 'field': 'onTransportBelt', 'index':0}),
                    html.Td('No data yet', className='value', id={'type':'synced', 'topic': 'f/i/state/sld', 'field': 'observedColor', 'index':0})
                ])
            ], className='device-data-table', id='sld-table'),
        ], className='sld'),
        dcc.Interval(id='updater', n_intervals=0, interval=0.5 * 1000) # every 0.5 seconds,
    ],
    className='factory-data'
)

@callback(
    Output('sld-table', 'children'),
    Input('updater', 'n_intervals'),
    State('sld-table', 'children')
)
def update_sld(n_intervals, el):    
    client = mqttClient.MqttClient()
    state_data = mqttClient.MqttClient.get_state(client, 'data')
    
    if (n_intervals != 0) and (not state_data['dirty']): # not "dirty" = nothing changed since last time it was called
        raise PreventUpdate
    else:    
        patch = Patch() # patch object of the sld-table children.
        
        lts = patch[1] # <tr> element for the lts data
        
        lts['children'] = [
                html.Td(state_data['f/i/state/sld'].get(v, 'No data yet'), className='value') 
                for v in ['active', 'error', 'errorMessage', 'workpieceID', 'workpieceType', 'onTransportBelt', 'observedColor']
            ]

        return patch

dash.register_page(__name__, path='/data', layout=layout)
