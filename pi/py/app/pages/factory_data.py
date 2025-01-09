import dash
from dash import Dash, html, Input, Output, State, callback, dcc, ALL, Patch
from dash.exceptions import PreventUpdate
import asyncio
import dash_daq as daq
import logging
from common import runtime_manager
from state import PageStateManager

layout = html.Div([
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
                html.Tr()
            ], className='device-data-table', id='sld-table'),
        ], className='sld')
    ],
    className='factory-data'
)

@callback(
    Output('sld-table', 'children'),
    Input('mqtt:state_sld', 'message'),
    State('sld-table', 'children')
)
def update_sld(state_sld, el):            
    patch = Patch() # patch object of the sld-table children.
    
    patch[1] = html.Tr([ # patch[1] is the first <tr> element, the 0th is the headers
            html.Td(str(state_sld.get(prop, 'No data yet')), className='value') 
            for prop in ['active', 'error', 'errorMessage']
        ] + [
            html.Td(str(state_sld.get('workpiece').get(workpieceProp, 'No data yet')), className='value') 
            for workpieceProp in ['id', 'type', 'state']
        ] + [
            html.Td(str(state_sld.get('workpiece').get('states').get(workpieceState, 'No data yet')), className='value') 
            for workpieceState in ['onTransportBelt', 'colorObserved']
        ]
    )

    return patch

dash.register_page(__name__, path='/factory-data', layout=layout)
