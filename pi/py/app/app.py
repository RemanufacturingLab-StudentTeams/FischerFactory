from dash import dcc, html, Dash
from dash.dependencies import Input, Output
import dash
import logger
from dotenv import load_dotenv
import page_icons

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
        dash.page_container,
    ],
    className='wrapper'
)


if __name__ == "__main__":
    load_dotenv()
    logger.setup()
    app.run_server(debug=True)
