from state import PageStateManager
from dash import html, dcc
from dash import page_registry, page_container

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
    await psm.monitor_page('global')
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
    
    return layout

layoutDebug = html.Div(
    [
        html.Button("debug", id="debug-button", n_clicks=0),
        html.Div(children="no clicks", id="debug-div"),
    ]
)