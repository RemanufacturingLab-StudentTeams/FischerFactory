import dash
from dash import Dash, html, Input, Output, callback, dcc, ALL, Patch
import logging

layout = html.Div([
    html.Button('debug', id='debug-button', n_clicks=0),
    html.Div('no clicks', id='debug-div')
])

@callback(
    Output('debug-div', 'children'),
    Input('debug-button', 'n_clicks')
)
def debugButton(n_clicks):
    logging.debug('click!')
    return f"button has been clicked {n_clicks} times."

dash.register_page(__name__, path='/debug', layout=layout)