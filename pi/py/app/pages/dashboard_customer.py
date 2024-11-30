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

layout = html.Div([
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
            dcc.Input(type='number', value=4000, debounce=True, step=100, id='order-baking-time')
        ]),
        html.Div([
            html.Label('Milling'),
            daq.ToggleSwitch(value=False, color='#0094CE', id='order-milling')
        ]),
        html.Div([
            html.Label('Milling time [ms]'),
            dcc.Input(type='number', value=4000, debounce=True, step=100, id='order-milling-time')
        ]),
        html.Button('ORDER', id='place-order', title="Disabled: please select a color.")
    ], className='order-config'),
    html.Div([
        html.H2('Order Queue'),
        html.Table([
            html.Tr([
                html.Th('Nr.'),
                html.Th('Colour'), # bo'el o' wo'uh
                html.Th('Oven'),
                html.Th('Milling')
            ])
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
def toggle_order_button(color_value):
    if color_value is None:
        return True, "Disabled: please select a color."
    return False, 'Click to place your order.'

@callback(
    [
        Output('place-order', 'className'),
        Output('place-order', 'disabled', allow_duplicate=True),
        Output('place-order', 'title', allow_duplicate=True)
    ],
    Input('place-order', 'n_clicks'),
    State('order-color', 'value'),
    State('order-baking', 'value'),
    State('order-baking-time', 'value'),
    State('order-milling', 'value'),
    State('order-milling-time', 'value'),
    prevent_initial_call = True
)
def place_order(n_clicks, color_picker_value, baking, baking_time, milling, milling_time):
    
    if color_picker_value is None:
        raise PreventUpdate
    
    logging.info(f'''[DASHBOARD_CUSTOMER] Placing order for puck 
        with colour {color_picker_value}
        {'which will be baked for ' + str(baking_time) if baking else 'which will not be baked'}
        {'which will be milled for ' + str(milling_time) if milling else 'which will not be milled'}
    ''')
    
    psm = PageStateManager()
    rtm = RuntimeManager()
    rtm.add_task(
        psm.send_data(
            page='dashboard-customer',
            keys_and_data={
                's_type': color_picker_value, # type of puck (i.e., colour)   
                'order_do_oven': baking,
                'order_oven_time': baking_time if baking else 0,
                'order_do_saw': milling,
                'order_saw_time': milling_time if milling else 0,
                'order_ldt_ts': datetime.now()
            }
            
        )
    )
    
    return 'pending', True, 'Disabled: Pending' # disables the button until the reset_buttons callback resets it.

@callback(
    [
        Output('place-order', 'className', allow_duplicate=True),
        Output('place-order', 'disabled', allow_duplicate=True),
        Output('place-order', 'title', allow_duplicate=True)
    ],
    Input('updater', 'n_intervals'),
    prevent_initial_call=True
)
def reset_buttons(n_intervals):
    """Resets greyed out buttons when it notices the call has been acknowledged. It does this by checking if the user-sent data has been set to clean (which the psm does when the call is awaited).
    """
    # Order button
    psm = PageStateManager()
    if psm.get_data('dashboard-customer', 'order_ldt_ts') is not None: # i.e., it is dirty, i.e., the user-sent data has been ack'ed
        return '', False, 'Click to place your order.' # reset the button
    else:
        raise PreventUpdate
