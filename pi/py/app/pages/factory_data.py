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
            html.Div([
                html.Span('Active', className='label'),
                html.P('No data yet', className='value', id={'type':'synced', 'topic': 'f/i/state/sld', 'field': 'active', 'index':0}), 
                html.Span('Error', className='label'),
                html.P('No data yet', className='value', id={'type':'synced', 'topic': 'f/i/state/sld', 'field': 'error', 'index':0}),
                html.Span('Error message', className='label'),
                html.P('No data yet', className='value', id={'type':'synced', 'topic': 'f/i/state/sld', 'field': 'errorMessage', 'index':0}),
                html.Span('Workpiece ID', className='label'),
                html.P('No data yet', className='value', id={'type':'synced', 'topic': 'f/i/state/sld', 'field': 'workpieceID', 'index':0}),
                html.Span('Workpiece type', className='label'),
                html.P('No data yet', className='value', id={'type':'synced', 'topic': 'f/i/state/sld', 'field': 'workpieceType', 'index':0}),
                html.Span('On transport belt', className='label'),
                html.P('No data yet', className='value', id={'type':'synced', 'topic': 'f/i/state/sld', 'field': 'onTransportBelt', 'index':0}),
                html.Span('Color', className='label'),
                html.P('No data yet', className='value', id={'type':'synced', 'topic': 'f/i/state/sld', 'field': 'observedColor', 'index':0})
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
def update(n_intervals, el):    
    client = mqttClient.MqttClient()
    state_data = mqttClient.MqttClient.get_state(client, 'data')
    
    
    if (n_intervals != 0) and (not state_data['dirty']): # "dirty" = nothing changed since last time it was called
        raise PreventUpdate
    else:    
        patch = Patch() # patch object of the sld-table children.
        
        for i in range(len(el)):
            logging.debug(el[i]['props'].get('id', {}).get('type', {}))
            if el[i]['props'].get('id', {}).get('type', {}) == 'synced':
                logging.debug(state_data[el[i]['props']['id']['topic']])
                topic = el[i]['props']['id']['topic']
                field = el[i]['props']['id']['field']
                patch[i]["props"]["children"] = state_data.get(topic, {}).get(field, "No data yet")
        return patch

dash.register_page(__name__, path='/data', layout=layout)
