from dash import Dash, html, Input, Output
from backend import opcuaClient
import asyncio

# Homepage
app = Dash(__name__)

app.layout = html.Div(
    className="main-container",
    children=[
        html.H1("Fischer Factory Dashboard", className="header-banner"),
        html.Button("CLEAR", id="clear-button", className="clear-button"),
        html.Div(id='feedback-div')
    ]
)

async def write_clear():
    async with opcuaClient.OPCUAClient() as c:
        await c.write('ns=3;s="gtyp_Setup"."x_Clean_Rack_HBW"', True)

@app.callback(
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
        
def runUI():
    app.run_server(debug=True)