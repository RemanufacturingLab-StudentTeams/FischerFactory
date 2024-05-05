#import packages
import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import os
import math
from PIL import Image

#create the dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

#get current dir for paths
current_directory = os.path.dirname(__file__)
def getPath(name):
    file_path = os.path.join(current_directory, name)
    return file_path

df_loc_path = getPath("Locations (B&W).csv")
print(df_loc_path)

factory_img_path = getPath("Assets/Fischer with colour masks, labels, and arrows (cropped, transparent background).png")


#df_puck_path = "C:/Users/antoi/Documents/TranSIT/Prototype 4 - Realistic Fischer Factory/"
#df_puck = pd.read_csv(df_puck_path)

#Open factory img
factory_img = Image.open(factory_img_path)

#to check if cells are empty
def notNaN(x):
    return x == x

#to get coordinates for pucks from dataset, returns % of img x, y
def getCoordsPer(df, x):
    coord_per_x = 100 * (df.loc[x, 'X_coord'] / factory_img.size[0])
    coord_per_y = 100 * (df.loc[x, 'Y_coord'] / factory_img.size[1])

    return coord_per_x, coord_per_y

#get different img for puck appearance based on values in df_loc
def getPuck(df, i):

    if (df.loc[i, 'Puck 1'])[0] =='R':
        puck_img_path = getPath("Assets/Puck_red.png")
    elif (df.loc[i, 'Puck 1'])[0] =='B':
        puck_img_path = getPath("Assets/Puck_blue.png")
    elif (df.loc[i, 'Puck 1'])[0] == 'W':
        puck_img_path = getPath("Assets/Puck_white.png")
    else:
        puck_img_path = getPath("Assets/Puck_green.png")

    puck_img = Image.open(puck_img_path)
    return puck_img

#create app layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([

            dbc.Row([
                dbc.Col([
                    html.H1("Factory floor", style={'textAlign': 'left',
                                                    'font-family': 'Arial, sans-serif',
                                                    'text-decoration': 'underline',
                                                    'font-size': 'xx-large',
                                                    'padding': '20px'})
                ], width=10),
                dbc.Col([html.Button("Refresh", id="Refresh-button", n_clicks=0,
                                     style={'text-align': 'center', 'padding': '5px', 'margin': '20px'})
                         ], width=2)
            ]),

            html.Div([
                html.Img(src=factory_img, id="Factory_img",
                         style={'width': '100%', 'height': '100%',
                                'object-fit': 'cover',
                                'border': '3px solid #73AD21'}),

                html.Div(id='Puck-container', children=[])

            ], style={'position': 'relative'})

        ], style={'position': 'relative'}, width=7),

        dbc.Col([
            html.H1("Product Information", style={'textAlign': 'center',
                                                    'font-family': 'Arial, sans-serif',
                                                    'text-decoration': 'underline',
                                                    'font-size': 'x-large',
                                                    'padding': '30px'}),

            #dash_table.DataTable(df_puck.to_dict('records'), [{"name": i, "id": i} for i in df_puck.columns],
                                 #id="puck_tbl",
                                 #fixed_rows={'headers': True},
                                 #style_table={'height': 400,
                                              #'border': '3px solid #73AD21',
                                              #'overflowX': 'auto',
                                              #'overflowY': 'auto'},
                                 #style_cell={'minWidth': '50px',
                                             #'width':'75px',
                                             #'maxWidth': '100px',
                                             #'whiteSpace': 'normal',
                                             #'height': 'auto'})
        ], width=5)
    ])
])

# The callback currently shows where the products (pucks are) more interesting is to show locations,
# which can be modified easily, with the ability to add new ones, and then to just check at which
# location each product is, to know what number to display for each.

# Important idea (but complicated to implement), would be the ability to "zoom" in on areas of the factory,
# could have a general view and then a zoomed in view for each section

@app.callback(
    Output(component_id='Puck-container', component_property='children'),
    [Input(component_id='Refresh-button', component_property='n_clicks')],
    prevent_initial_call=False
)

def update_pucks(n_clicks):
    df_loc = pd.read_csv(df_loc_path)
    puck_elements = []
    for index, row in df_loc.iterrows():
        if notNaN(row['Puck 1']):
            x, y = getCoordsPer(df_loc, index)
            puck_img = getPuck(df_loc, index)
            text = str(row['Puck 1'])

            puck_element = html.Button(
                id={'type': 'puck', 'index': index},
                children=[
                    html.Img(src=puck_img, style={'width': '60%', 'height': '60%'}
                    ),
                    html.P(text, style={'position': 'absolute', 'top': '50%', 'left': '50%',
                                        'transform': 'translate(-50%, -50%)', 'font-size': 'xx-small'})
                ],
                style={
                    'position': 'absolute',
                    'top': f'{y}%',
                    'left': f'{x}%',
                    'transform': 'translate(-50%, -50%)',
                    'padding': '0',
                    'margin': '0',
                    'background-color': 'transparent',
                    'border': 'none',
                    'cursor': 'pointer'
                }
            )

            puck_elements.append(puck_element)

    return puck_elements

#@app.callback(
    #Output('puck_tbl', 'children'),
    #[Input({'type': 'puck', 'index': ALL}, 'n_clicks')],
    #[State({'type': 'puck', 'index': ALL}, 'id')]
#)

#return table

if __name__ == '__main__':
    app.run_server(debug=True)
