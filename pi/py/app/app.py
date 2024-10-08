from dash import dcc, html, Dash
from dash.dependencies import Input, Output
import dash
import logger
import logging
from dotenv import load_dotenv
import page_icons
import os, argparse
from backend import mqttClient
import asyncio

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the application.')
    parser.add_argument('--dev', action='store_true', help='Run in development mode')
    dev = parser.parse_args().dev
    os.environ.clear()
    
    load_dotenv(dotenv_path=('.env-dev' if dev else '.env-prod'))
    print(f"Running in {'development' if dev else 'production'} mode with environment variables: {os.environ}")
    
    logger.setup()
    
    async def testClient():
        # Initialize the MQTT client
        client = mqttClient.MqttClient()

        # Keep the event loop running
        await asyncio.Future()  
            
    asyncio.run(testClient())
    
    app.run(dev_tools_hot_reload=bool(dev))
    