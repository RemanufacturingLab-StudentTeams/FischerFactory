from dash import html, callback, Input, Output, State
from state import PageStateManager
from dash.exceptions import PreventUpdate
import logging

hbw_view = html.Div(
    [
        html.H2('HBW View'),
        html.Div([
# dynamically generated
        ], className='hbw-view-container button-menu', id='hbw-view-container')
    ],
    className='hbw-view'
)

@callback(
    Output('hbw-view-container', 'children'),
    Input({'source': 'mqtt', 'key': 'stock'}, 'message'),
    prevent_initial_call=True
)
def display_hbw(stock, state):    
    logging.debug(f'display_hbw called with {stock}')
    
    if stock is None:
        raise PreventUpdate
    
    buttons = [
        (
            html.Div(
                stock['stockItem'][f'{x},{y}']['id'],
                className='puck-' + stock['stockItem'][f'{x},{y}']['type'].lower() # class names will become 'puck-red', 'puck-blue', 'puck-white' or 'empty'
            )
            if stock['stockItem'][f'{x},{y}'].get('type', False)
            else html.Div(className='puck-empty')
        )
            for x in range(3)
            for y in range(3)
    ]
    
    return [
            html.Div(),
            html.Span('1', className='label'),
            html.Span('2', className='label'),
            html.Span('3', className='label'),
            html.Span('A', className='label'),
            *buttons[0:3], # button 0 to 3 exclusive, so the first 3
            html.Span('B', className='label'),
            *buttons[3:6],
            html.Span('C', className='label'),
            *buttons[6:9]
    ]

__all__ = ['hbw_view', 'display_hbw']