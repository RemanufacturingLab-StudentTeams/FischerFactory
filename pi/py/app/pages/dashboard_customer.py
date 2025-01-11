import dash
from dash import Dash, html, Input, Output, State, callback, dcc, ALL, Patch, page_registry
import dash_daq as daq
import logging
from pages.components import hbw_view, display_hbw
from state import PageStateManager
from datetime import datetime, timezone
from dash.exceptions import PreventUpdate
from common import RuntimeManager
import json

async def generate_layout() -> html.Div:
    psm = PageStateManager()
    layout = html.Div(
        (await psm.generate_websockets('dashboard-customer')) + 
        [dcc.Store(storage_type='memory', id='order-store'), # used to remember the orders the customer placed. 
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
            ], id='baking-time'),
            html.Div([
                html.Label('Milling'),
                daq.ToggleSwitch(value=False, color='#0094CE', id='order-milling')
            ]),
            html.Div([
                html.Label('Milling time [ms]'),
                dcc.Input(type='number', value=4000, debounce=True, step=100, id='order-milling-time')
            ], id='milling-time'),
            html.Button('ORDER', id='place-order', title="Disabled: please select a color.")
        ], className='order-config'),
        html.Div([
            html.H2('Order Queue'),
            html.Table([
    # dynamically generated
        ], id='order-queue-table', className='data-table')
        ], className='order-queue'),
        hbw_view,
        html.Div([
            html.H2('Order State'),
            html.Div([
                html.Span('Ordered at', className='label'),
                html.P('Loading...', className='value'),
                html.Span('State', className='label'),
                html.P('Loading...', className='value'),
                html.Span('Colour', className='label'),
                html.P('Loading...', className='value')
            ], className='state-order table', id='state-order-table')
        ], className='state-order-container'),
        html.Div([
            html.H2('Tracking'),
            html.Div([
                html.Span('Location', 'label'),
                html.P('Loading...', className='value', id='tracking')
            ], className='tracking table')
        ], className='tracking-container')
    ], className='dashboard-customer')

    @callback(
        Output('place-order', 'disabled'),
        Output('place-order', 'title'),
        Input('order-color', 'value'),
        Input('mqtt:queue', 'message')
    )
    def validate_order_button(color_value, queue):
        if color_value is None:
            return True, "Disabled: please select a color."
        psm = PageStateManager()
        queue_full: bool = queue['queue']['queueFull']
        if queue_full:
            return True, "Disabled: Queue is full."
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
        
        psm = PageStateManager()
        rtm = RuntimeManager()
        rtm.add_task(
            psm.send_data(
                page='dashboard-customer',
                data={
                    's_type': color_picker_value.upper(), # type of puck (i.e., colour)   
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
        Output('baking-time', 'className'),
        Output('milling-time', 'className'),
        Input('order-baking', 'value'),
        Input('order-milling', 'value')
    )
    def hide_time_fields(order_baking, order_milling):
        return 'hidden' if not order_baking else '', 'hidden' if not order_milling else ''

    # !TODO: Ack and error handling mechanism
    # @callback(
    #     [
    #         Output('place-order', 'className', allow_duplicate=True),
    #         Output('place-order', 'disabled', allow_duplicate=True),
    #         Output('place-order', 'title', allow_duplicate=True)
    #     ],
    #     Input('updater', 'n_intervals'),
    #     prevent_initial_call=True
    # )
    # def reset_buttons(n_intervals):
    #     """Resets greyed out buttons when it notices the call has been acknowledged. It does this by checking if the user-sent data has been set to clean (which the psm does when the call is awaited).
    #     """
    #     # Order button
    #     psm = PageStateManager()
    #     if psm.get('dashboard-customer', 'order_ldt_ts') is not None: # i.e., it is dirty, i.e., the user-sent data has been ack'ed
    #         return '', False, 'Click to place your order.' # reset the button
    #     else:
    #         raise PreventUpdate

    @callback(
        Output('state-order-table', 'children'), 
        Input('mqtt:state_order', 'message')
    )
    def display_order(state_order):
        psm = PageStateManager()
        ts = state_order['ts']
        state = state_order['state']
        color = state_order['type']
        
        patch = Patch()
        if ts:
            patch[1]['props']['children'] = ts.strftime("%m/%d/%Y, %H:%M:%S")
        if state:
            patch[3]['props']['children'] = state
        if color:
            patch[5]['props']['children'] = color
        
        return patch

    @callback(
        Output('order-queue-table', 'children'),
        Input('mqtt:queue', 'message')
    )
    def display_queue(queue):
        psm = PageStateManager()
        queue_index: int = queue['queueIndex'] or 0
        queue_full: bool = queue['queue']['queueFull'] or False
        
        return [
            html.Tr([
                    html.Th('Nr.'),
                    html.Th('Colour'), # bo'el o' wo'uh
                    html.Th('Oven'),
                    html.Th('Milling'),
                    html.Th('Ordered at')
                ])
            
        ] + [
            html.Tr([
                html.Td(index + 1),
                html.Td(puck['type']),
                html.Td(puck['parameters']['ovenTime'] if puck['parameters']['doOven'] else 'No'),
                html.Td(puck['parameters']['sawTime'] if puck['parameters']['doSaw'] else 'No'),
                html.Td(puck['ts'].strftime("%m/%d/%Y, %H:%M:%S"))
            ])
            for index, puck in enumerate(queue['queue'][:queue_index])
        ] + ([
            html.Tr('QUEUE FULL', className='queue-full-banner')
        ] if queue_full else [])

    @callback(
        Output('tracking', 'children'),
        Input('mqtt:tracking', 'message')
    )
    def display_tracking(tracking):
        tracking = tracking.get('trackPuck')
        if not tracking:
            raise PreventUpdate
        return tracking
        
    display_hbw # callback function defined in `pages/components/hbw_view.py`.
    
    return layout

async def register():
    layout = await generate_layout()
    dash.register_page(
        __name__, 
        path='/dashboard-customer', 
        layout=layout
    )
    logging.debug(f'Registered page {__name__}')

