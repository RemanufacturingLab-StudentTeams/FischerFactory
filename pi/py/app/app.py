import pprint
from dash import dcc, html, Dash, Input, Output
import dash
import logger
from dotenv import load_dotenv
import page_icons
import os, argparse
from backend import mqttClient, opcuaClient
import asyncio
from threading import Thread

app = Dash(__name__, 
                external_stylesheets=[
                    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"
                    ],
                use_pages=True
                )

# Global layout for the app
app.layout = html.Div(
    [
        html.Div(
            'FischerFactory Dash Dashboard',
            id='banner-title',
            className='banner title'
            ),
        html.Div(
            [
                html.Div([
                    html.I(className=page_icons.i[page['name']], style={"margin": "5px"}),
                    dcc.Link(
                        f"{page['name']}", href=(page["relative_path"])
                    )
                    ],
                    className='side-panel-link'
                )
                for page in dash.page_registry.values()
                if page["module"] != "pages.not_found_404"
            ],
            className='side-panel',
        ),
        html.Div(
            id='feedback-div'
        ),
        html.Div([
            dash.page_container,
            ],
            className='page-content'   
        )
    ],
    className='wrapper'
)

layoutDebug = html.Div([
    html.Button('debug', id='debug-button', n_clicks=0),
    html.Div('no clicks', id='debug-div')
])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the application.')
    parser.add_argument('--dev', action='store_true', help='Run in development mode')
    dev = parser.parse_args().dev
    os.environ.clear()
    
    load_dotenv(dotenv_path=('.env-dev' if dev else '.env-prod'))
    print(f"Running in \033[0;33m{'development' if dev else 'production'} mode\033[0m with environment variables:")
    pprint.pprint(os.environ.copy())
    
    logger.setup()
    
    async def startClients():
        # Initialize the MQTT client
        mqtt = mqttClient.MqttClient()
        opcua = opcuaClient.OPCUAClient()
        
        # Keep the event loop running
        await asyncio.Future()
        
    def asyncWrapper():
        asyncio.run(startClients()) 
    
    # Start OPCUA and MQTT Clients (important: *before* starting the app!)
    th = Thread(target=asyncWrapper)
    th.start()
    
    # Launch the Dash app
    app.run(dev_tools_hot_reload=bool(dev), debug=False)
    
    th.join()