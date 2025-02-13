import dash
from dash import (
    Dash,
    html,
    Input,
    Output,
    State,
    callback,
    dcc,
    ALL,
    Patch,
    page_registry,
)
import dash_daq as daq
from dash_extensions import WebSocket
import logging
from pages.components import hbw_view, display_hbw
from datetime import datetime, timezone
from dash.exceptions import PreventUpdate
from common import RuntimeManager
import json
import os
from backend import MqttClient
from common import format_time_string

layout = html.Div(
    [
        *[WebSocket(
            id={"source": "mqtt", "topic": topic},
            url=f"ws://localhost:8765/{topic}",
        ) for topic in ['f/queue', 'f/i/order', 'f/i/track', 'f/o/order/response']],
        dcc.Store(
            storage_type="memory", id="order-store"
        ),  # used to remember the orders the customer placed.
        html.Div(
            [
                html.Link(href="../assets/customer.css", rel="stylesheet"),
                html.H2("Order Configuration"),
                html.Div(
                    [
                        html.Label("Colour picker"),  # Bri'ish colour
                        dcc.Dropdown(
                            options=["Red", "White", "Blue"],
                            id="order-color",
                            value=None,
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Label("Baking"),
                        daq.ToggleSwitch(
                            value=False, color="#0094CE", id="order-baking"
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Label("Baking time [ms]"),
                        dcc.Input(
                            type="number",
                            value=4000,
                            debounce=True,
                            step=100,
                            id="order-baking-time",
                        ),
                    ],
                    id="baking-time",
                ),
                html.Div(
                    [
                        html.Label("Milling"),
                        daq.ToggleSwitch(
                            value=False, color="#0094CE", id="order-milling"
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Label("Milling time [ms]"),
                        dcc.Input(
                            type="number",
                            value=4000,
                            debounce=True,
                            step=100,
                            id="order-milling-time",
                        ),
                    ],
                    id="milling-time",
                ),
                html.Button(
                    "ORDER", id="place-order", title="Disabled: please select a color."
                ),
            ],
            className="order-config",
        ),
        html.Div(
            [
                html.H2("Order Queue"),
                html.Table(
                    [
                        # dynamically generated
                    ],
                    id="order-queue-table",
                    className="data-table",
                ),
            ],
            className="order-queue",
        ),
        hbw_view,
        html.Div(
            [
                html.H2("Order State"),
                html.Div(
                    children=[], # dynamically generated by callback
                    className="state-order table",
                    id="state-order-table",
                ),
            ],
            className="state-order-container",
        ),
        html.Div(
            [
                html.H2("Tracking"),
                html.Div(
                    [
                        html.Span("Location", "label"),
                        html.P("Loading...", className="value", id="tracking"),
                    ],
                    className="tracking table",
                ),
            ],
            className="tracking-container",
        ),
    ],
    className="dashboard-customer",
)

@callback(
    Output("place-order", "disabled"),
    Output("place-order", "title"),
    Input("order-color", "value"),
    Input({"source": "mqtt", "topic": "f/queue"}, "message"),
)
def validate_order_button(color_value, queue):
    if color_value is None:
        return True, "Disabled: please select a color."
    if queue is None:
        raise PreventUpdate
    queue = json.loads(queue.get('data'))
    queue_full: bool = queue["queueFull"]
    if queue_full:
        return True, "Disabled: Queue is full."
    return False, "Click to place your order."

@callback(
    Output("order-baking-time", "style"), 
    Input("order-baking", "value")
)
def show_baking_time(do_baking):
    return (
        {"display": "flex"} if do_baking else {"display": "none"}
    )  # set hidden to True if baking is False, otherwise set hidden to False


@callback(
    Output("order-milling-time", "style"), 
    Input("order-milling", "value")
)
def show_baking_time(do_milling):
    return {"display": "flex"} if do_milling else {"display": "none"}

@callback(
    [
        Output("place-order", "className", allow_duplicate=True),
        Output("place-order", "disabled", allow_duplicate=True),
        Output("place-order", "title", allow_duplicate=True)
    ],
    Input("place-order", "n_clicks"),
    State("order-color", "value"),
    State("order-baking", "value"),
    State("order-baking-time", "value"),
    State("order-milling", "value"),
    State("order-milling-time", "value"),
    prevent_initial_call=True
)
def place_order(
    n_clicks,
    color_picker_value,
    baking,
    baking_time,
    milling,
    milling_time
):
    if color_picker_value is None:
        raise PreventUpdate

    logging.info(
        f"""Placing order for puck 
            with colour {color_picker_value}
            {'which will be baked for ' + str(baking_time) if baking else 'which will not be baked'}
            {'which will be milled for ' + str(milling_time) if milling else 'which will not be milled'}
        """
    )

    rtm = RuntimeManager()
    mqtt_client = MqttClient()
    rtm.add_task(
        mqtt_client.publish(
            topic="f/o/order",
            payload={
                "type": color_picker_value.upper(),  # type of puck (i.e., colour)
                "workpieceParameters": {
                    "doOven": baking,
                    "ovenTime": baking_time if baking else 0,
                    "doSaw": milling,
                    "sawTime": milling_time if milling else 0,
                },
                "ts": datetime.now(),
            },
        )
    )

    return ("pending",True,"Disabled: Pending")

@callback(
    [
        Output("place-order", "className", allow_duplicate=True),
        Output("place-order", "disabled", allow_duplicate=True),
        Output("place-order", "title", allow_duplicate=True)
    ],
    Input({"source": "mqtt", "topic": "f/o/order/response"}, "message"),
    prevent_initial_call=True
)
def resetPlaceOrder(message):
    """Resets the place order button when the relay sends a response.
    """
    message = json.loads(message.get('data'))
    if message.get('err'):
        logging.error(message.get('err'))
    else:
        logging.info(message.get('msg'))
    return ('label', False, '')

@callback(
    Output("baking-time", "className"),
    Output("milling-time", "className"),
    Input("order-baking", "value"),
    Input("order-milling", "value"),
)
def hide_time_fields(order_baking, order_milling):
    return "hidden" if not order_baking else "", "hidden" if not order_milling else ""

@callback(
    Output("state-order-table", "children"), 
    Input({"source": "mqtt", "topic": "f/i/order"}, "message"))
def display_state_order(state_order):
    
    if state_order is None:
        raise PreventUpdate
    
    state_order= json.loads(state_order.get('data'))
    ts = format_time_string(state_order.get('ts')) if state_order.get('ts') else ''
    state = state_order["state"] or 'Loading...'
    color = state_order["type"] or ''

    return [
        html.Span("Ordered at", className="label"),
        html.P(ts, className="value"),
        html.Span("State", className="label"),
        html.P(state, className="value"),
        html.Span("Colour", className="label"),
        html.P(color, className="value"),
    ]


@callback(
    Output("order-queue-table", "children"), 
    Input({"source": "mqtt", "topic": "f/queue"}, "message"),
    prevent_initial_call=True)
def display_queue(queue):
    if queue is None:
        raise PreventUpdate
    
    queue = json.loads(queue.get('data'))
    queue_index: int = queue["queueIndex"] or 0
    queue_full: bool = queue["queueFull"] or False

    print(queue['queue'][0]['ts'])
    print(type(queue['queue'][0]['ts']))

    return (
        [
            html.Tr(
                [
                    html.Th("Nr."),
                    html.Th("Colour"),  # bo'el o' wo'uh
                    html.Th("Oven"),
                    html.Th("Milling"),
                    html.Th("Ordered at"),
                ]
            )
        ]
        + [
            html.Tr(
                [
                    html.Td(index + 1),
                    html.Td(puck["type"]),
                    html.Td(
                        puck["parameters"]["ovenTime"]
                        if puck["parameters"]["doOven"]
                        else "No"
                    ),
                    html.Td(
                        puck["parameters"]["sawTime"]
                        if puck["parameters"]["doSaw"]
                        else "No"
                    ),
                    html.Td(format_time_string(puck['ts']) if puck.get('ts') else ''),
                ]
            )
            for index, puck in enumerate(queue["queue"][:queue_index])
        ]
        + ([html.Tr("QUEUE FULL", className="queue-full-banner")] if queue_full else [])
    )

@callback(
        Output("tracking", "children"), 
        Input({"source": "mqtt", "topic": "f/i/track"}, "message"),
        prevent_initial_call=True
    )
def display_tracking(tracking):
    
    if tracking is None or tracking == "":
        raise PreventUpdate
    
    tracking = json.loads(tracking.get('data'))
    
    return tracking['trackPuck']

display_hbw  # callback function defined in `pages/components/hbw_view.py`.

dash.register_page(__name__, path="/dashboard-customer", layout=layout)
