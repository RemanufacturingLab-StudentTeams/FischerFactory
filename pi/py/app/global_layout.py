from state import PageStateManager
from dash import html, dcc, callback, Input, Output, ALL
from dash import page_registry, page_container
from backend import MqttClient
from common import RuntimeManager
import os

# Global layout for the app
page_icons = {
    "Factory overview": "fas fa-home",
    "Factory data": "fas fa-bar-chart",
    "Dashboard customer": "fas fa-solid fa-cart-shopping",
    "Debug": "fa fa-bug",
}

async def layout():
    psm = PageStateManager()
    await psm.hydrate_page('global')
    layout = html.Div(
        await psm.generate_websockets('global') +
        [
            dcc.Location('location', refresh=True),
            html.Div(
                [
                    html.Div("FischerFactory Dash Dashboard"),
                    html.Div(
                        [
                            html.Div(
                                [], id="mqtt-broker-status", className="connection-status"
                            )
                        ],
                        className="status-container",
                    ),
                ],
                id="banner-title",
                className="banner title",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.I(
                                className=page_icons[page["name"]], style={"margin": "5px"}
                            ),
                            dcc.Link(f"{page['name']}", href=(page["relative_path"]), refresh=True),
                        ],
                        className="side-panel-link",
                    )
                    for page in page_registry.values()
                    if page["module"] != "pages.not_found_404"
                ],
                className="side-panel",
            ),
            html.Div(id="feedback-div"),
            html.Div([], id="dummy"),
            html.Div(
                [
                    page_container,
                ],
                className="page-content",
            ),
            dcc.Interval(id="updater", n_intervals=0, interval=2 * 1000), # 2 second interval
        ],
        className="wrapper",
    )
    
    @callback(
        [Output("mqtt-broker-status", "children"), Output("mqtt-broker-status", "style")],
        Input("updater", "n_intervals"),
    )
    def update_status_mqtt(n_intervals):
        client = MqttClient()
        status_text = f"MQTT Broker at {os.getenv('MQTT_BROKER_IP')}: "

        if client.get_status():
            status_text += "OK"
            style = {
                "backgroundColor": "green",
                "color": "white",
            }
        elif client.get_reconnection_attempts() < 10:
            status_text += (
                f"Reconnecting... {client.get_reconnection_attempts()}/10 attempts"
            )
            style = {
                "backgroundColor": "yellow",
                "color": "black",
            }
        else:
            status_text += "Disconnected"
            style = {
                "backgroundColor": "red",
                "color": "white",
            }

        return status_text, style

    @callback(
        Output(
            component_id={'source': 'ws', 'path': ALL}, 
            component_property="send"
        ),
        Input("location", "href")
    )
    def switch_page(href: str):
        import logging # bit weird to not put this import at the top of the page but the logger setup really needs to run first so ¯\_(ツ)_/¯
        # page_name = pathname.lstrip('/') or 'factory-overview'
        page_name = href.split('/')[-1].split('?')[0] or 'factory-overview'
        
        logging.debug(f"Switched to page: {page_name}")
        
        psm = PageStateManager()
        rtm  = RuntimeManager()
            
        rtm.add_task(psm.hydrate_page(page_name))
        
        return 'connect' # send connect signal over WebSockets
    
    return layout
