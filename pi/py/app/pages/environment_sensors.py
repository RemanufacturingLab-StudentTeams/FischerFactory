import dash
from dash import html, dcc, Input, Output, State, callback
from dash_extensions import WebSocket
from dash.exceptions import PreventUpdate
import json
from datetime import date, datetime
import plotly.graph_objs as go

layout = html.Div(
    [
        *[
            WebSocket(
                id={"source": "mqtt", "topic": topic},
                url=f"ws://10.35.4.254:8765/{topic}",
            )
            for topic in ["i/bme680", "i/ldr"]
        ],
        
        html.Link(href="../assets/sensors.css", rel="stylesheet"),
        
        html.H2("BME680 Data"),
        html.Div(id="bme680-graph-container"),
        html.H2("Photoresistor Data"),
        html.Div(id="photoresistor-graph-container")
    ],
    className="environment-sensors",
)

bme680_measurements = {"timestamps": [], "t": [], "p": [], "iaq": [], "h": []}

names_and_units = {
    "t": {"name": "Temperature", "unit": "°C"},
    "p": {"name": "Pressure", "unit": "hPa"},
    "iaq": {"name": "Air Quality Index", "unit": "0-500 (Lower is better)"},
    "h": {"name": "Humidity", "unit": "%"},
}

@callback(
    Output("bme680-graph-container", "children"),
    Input({"source": "mqtt", "topic": "i/bme680"}, "message"),
)
def graph_bme680(measurement):
    if measurement is None:
        raise PreventUpdate

    measurement_data = json.loads(measurement.get("data"))
    res = []

    for property in bme680_measurements.keys():
        if property == "timestamps":
            bme680_measurements["timestamps"].append(
                datetime.fromisoformat(measurement_data["ts"])
            )
        else:
            bme680_measurements[property].append(measurement_data[property])

            figure = go.Figure()
            figure.add_trace(
                go.Scatter(
                    x=bme680_measurements["timestamps"],
                    y=bme680_measurements[property],
                    mode="lines+markers",
                    name=names_and_units[property]["name"],
                )
            )
            figure.update_layout(
                title=f"{names_and_units[property]['name']} over time",
                xaxis_title='Time',
                yaxis_title=f"{names_and_units[property]['name']} [{names_and_units[property]['unit']}]",
            )
            res.append(dcc.Graph(figure=figure))

    return res

photoresistor_measurements = {"timestamps": [], "br": [], "ldr": []}

ldr_names_and_units = {
    "br": {"name": "Brightness", "unit": "0..100.0"},
    "ldr": {"name": "Resistance", "unit": "Ω"}
}

@callback(
    Output("photoresistor-graph-container", "children"),
    Input({"source": "mqtt", "topic": "i/ldr"}, "message"),
)
def graph_ldr(measurement):
    if measurement is None:
        raise PreventUpdate

    measurement_data = json.loads(measurement.get("data"))
    res = []

    for property in photoresistor_measurements.keys():
        if property == "timestamps":
            photoresistor_measurements["timestamps"].append(
                datetime.fromisoformat(measurement_data["ts"])
            )
        else:
            photoresistor_measurements[property].append(measurement_data[property])

            figure = go.Figure()
            figure.add_trace(
                go.Scatter(
                    x=photoresistor_measurements["timestamps"],
                    y=photoresistor_measurements[property],
                    mode="lines+markers",
                    name=ldr_names_and_units[property]["name"],
                )
            )
            figure.update_layout(
                title=f"{ldr_names_and_units[property]['name']} over time",
                xaxis_title='Time',
                yaxis_title=f"{ldr_names_and_units[property]['name']} [{ldr_names_and_units[property]['unit']}]",
            )
            res.append(dcc.Graph(figure=figure))

    return res


dash.register_page(__name__, path="/environment-sensors", layout=layout)
