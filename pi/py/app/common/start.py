"""Hey, modularity! This module is here so that starting resources are accessible anywhere in the program, and to fix circular dependencies that happened when this was in `app/app.py`. 
"""

from dash import Dash

app = Dash(__name__, 
                external_stylesheets=[
                    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"
                    ],
                use_pages=True,
                pages_folder='../pages',
                assets_folder='../assets',
                )

# Exports
__all__ =["app"]