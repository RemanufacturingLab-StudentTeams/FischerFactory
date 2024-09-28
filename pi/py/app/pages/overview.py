import dash
from dash import Dash, html, Input, Output, callback, dcc
from backend import opcuaClient
import asyncio

layout = html.Div(
    className="page-content",
    children=[

        html.Button("CLEAR", id="clear-button", className="clear-button"),
    ]
)

dash.register_page(__name__, path='/', redirect_from=['/overview'], layout=layout)

async def write_clear():
    async with opcuaClient.OPCUAClient() as c:
        await c.write('ns=3;s="gtyp_Setup"."x_Clean_Rack_HBW"', True)

@callback(
    Output('feedback-div', 'children'),
    Input('clear-button', 'n_clicks'),
)
def clean_rack_HBW(n_clicks):
    if n_clicks is not None:
        try:
            asyncio.run(write_clear())
        except Exception as e:
            return str(e)
        return "Rack cleared"
    return ""
