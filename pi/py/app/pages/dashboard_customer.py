import dash
from dash import Dash, html, Input, Output, State, callback, dcc, ALL, Patch
import dash_daq as daq
from backend import opcuaClient, mqttClient
import logging
from pages.components import hbw_view 
from state import PageStateManager
from datetime import datetime, timezone
from dash.exceptions import PreventUpdate
from common import RuntimeManager
import json

layout = html.Div([
    dcc.Store(storage_type='memory', id='order-store'), # used to remember the orders the customer placed. 
    html.Div([
        html.Link(href='../assets/customer.css', rel='stylesheet'),
        html.H2('Order Configuration'),
        html.Div([
            html.Label('Colour picker'), # Bri'ish colour
            dcc.Dropdown(options=['Red','White','Blue'], id='order-color', value=None)
        ]),
        html.Div([
            html.Label('Baking'),
            daq.ToggleSwitch(value=False, color='#0094CE', id='order-baking')
        ]),
        html.Div([
            html.Label('Baking time [ms]'),
            dcc.Input(type='number', value=4000, min=100, max=20000, debounce=True, step=100, id='order-baking-time')
        ], id='order-baking-time-container'),
        html.Div([
            html.Label('Milling'),
            daq.ToggleSwitch(value=False, color='#0094CE', id='order-milling')
        ]),
        html.Div([
            html.Label('Milling time [ms]'),
            dcc.Input(type='number', value=4000, min=100, max=20000, debounce=True, step=100, id='order-milling-time')
        ], id='order-milling-time-container'),
        html.Button('ORDER', id='place-order', title="Disabled: please select a color.")
    ], className='order-config'),
    html.Div([
        html.H2('Order Queue'),
        html.Table([
# dynamically generated
        ], id='order-queue-table', className='data-table')
    ], className='order-queue'),
    hbw_view,
], className='dashboard-customer')

dash.register_page(__name__, path='/dashboard-customer', layout=layout)

@callback(
    Output('place-order', 'disabled'),
    Output('place-order', 'title'),
    Input('order-color', 'value')
)
def validate_order(color_value):
    if color_value is None:
        return True, "Disabled: please select a color."
    return False, 'Click to place your order.'

@callback(
    Output('order-baking-time-container', 'style'),
    Input('order-baking', 'value')
)
def show_baking_time(do_baking):
    return {'display': 'flex'} if do_baking else {'display': 'none'} # set hidden to True if baking is False, otherwise set hidden to False

@callback(
    Output('order-milling-time-container', 'style'),
    Input('order-milling', 'value')
)
def show_baking_time(do_milling):
    return {'display': 'flex'} if do_milling else {'display': 'none'}

@callback(
    [
        Output('order-store', 'data')
    ],
    Input('place-order', 'n_clicks'),
    State('order-color', 'value'),
    State('order-baking', 'value'),
    State('order-baking-time', 'value'),
    State('order-milling', 'value'),
    State('order-milling-time', 'value'),
    State('order-store', 'data'),
    prevent_initial_call = True
)
def place_order(n_clicks, color_picker_value, baking, baking_time, milling, milling_time, current_orders):
    
    if color_picker_value is None:
        raise PreventUpdate
    
    logging.info(f'''[DASHBOARD_CUSTOMER] Placing order for puck 
        with colour {color_picker_value}
        {'which will be baked for ' + str(baking_time) if baking else 'which will not be baked'}
        {'which will be milled for ' + str(milling_time) if milling else 'which will not be milled'}
    ''')
    
    return [((current_orders or []) + [{
        'colour': color_picker_value,
        'baking': baking,
        'baking_time': baking_time if baking else 0,
        'milling': milling,
        'milling_time': milling_time if milling else 0,
    }])]

@callback(
    Output('order-queue-table', 'children'),
    Input('order-store', 'data')
)
def update_queue(orders):
    
    if not orders:
        raise PreventUpdate
    
    res = [
        html.Tr([
            html.Th('Nr.'),
            html.Th('Colour'), # bo'el o' wo'uh
            html.Th('Oven'),
            html.Th('Milling'),
            html.Th('Status'),
            html.Th('Tracking')
        ])
    ] 
    res += [html.Tr([
            html.Td(i),
            html.Td(order['colour']),
            html.Td(order['baking_time'] if order['baking'] else 'No'),
            html.Td(order['milling_time'] if order['milling'] else 'No'),
            html.Td('IN_QUEUE'),
            html.Td('IN_QUEUE')
        ]) for i, order in enumerate(orders)]
    
    return res