import dash
from dash import Dash, html, Input, Output, State, callback, dcc, ALL, Patch
from backend import opcuaClient, mqttClient
import logging

layout = ''

dash.register_page(__name__, path='/dashboard-customer', layout=layout)