# Python FischerFactory Dashboard

A dashboard made entirely in Python, made to monitor and control the FischerFactory stations and related sensors and devices (BME680, Photoresistorm, NFC Reader, Turtlebot). 

## Requirements

To run, this dashboard requires:
- Linux Bash
- Python 3.12.8
- Pip 24.3.1
- Pipenv 2024.4.0

Further requirements are found in the `Pipenv` file. These can be automatically installed if the requirements above are provided. 

## Environment variables

Two environment files exist: `.env.dev` and `.env.prod`. The former is used when running the program with the `--dev` argument (that is, not running it with the run script, but with `pipenv run python app/app.py --dev`). It is required that all of these variables have a value, or the program might exhibit undefined behaviour.

Key | Example value | Possible values | Explanation
|-|-|-|
MQTT_BROKER_IP | 10.35.4.253 | | IP address of the TXT broker on the `iotroam` network.
MQTT_BROKER_PORT | 1883 | |  Port of the TXT broker on the `iotroam` network.
MQTT_USERNAME | pi | | Username that the dashboard program uses to establish the MQTT connection with the broker.
MQTT_PASSWORD | pi | | Password that the dashboard program uses to establish the MQTT connection.
MQTT_RELAY_TOPIC | relay | | Topic that the PLC Relay functions on (see `pi/py/relay`).
PORT | 8050 | | Port that the dashboard will be accessible on for users.
WS_PORT | 8765 | | WebSocket port that the dashboard uses to send data to the frontend callbacks.
LOG_LEVEL | DEBUG | DEBUG, INFO, ERROR, CRITICAL | The minimum level of importance a log message must have to be shown. For example, if set to INFO (recommended for production), it will display INFO, ERROR and CRITICAL messages, but not DEBUG messages.
LOG_MESSAGES | TRUE | TRUE, FALSE, FILE | Log *incoming* MQTT and OPCUA messages. Setting this to TRUE generates a *lot* of logs. If set to FILE, it will only log to `logs/external_logs`.
PROJECT_ROOT_PATH | /home/wsladmin/FischerFactory | | This value is inserted/updated by the run.sh script. 

If these values are changed, the program should restart to apply the changes. 

## Running the program

A script to run everything, including installing the necessary libraries, exists as `run.sh`. When running it for the first time, do `chmod +x run.sh` to make it executable, then run it with `./run.sh`. This should open the application on `localhost:8050`. It can be accessed by other devices on the `iotroam` network on the IP address of the device that runs it (see the Networking section of the top-leven README for static IP addresses).

*Note: in the future, this program may be containerized to allow Docker to run it.*

## Logs, configs and other external files

If the `LOG_MESSAGES` is set to TRUE or FILE, the program will write log messages to `pi/py/logs/external_logs`. *Make sure to include them in the `.gitignore`.*

An options exists to download the running configuration of the FischerFactory to a `json` file. 

*!TODO: IMPLEMENT THIS*

## General Architecture and Dataflow

See `pi/py/diagram.uxf` for a high-level overview in the form of an (informal) UML diagram. (Note: it was made using the `UMLet` extension for VSCode, it will open with that). It shows the general dataflow in the FischerFactory. In general:

1. The PLC makes its data accessible on a OPCUA Node. (e.g.: `ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_VGR"."x_Start_Park_Position"` as a `Boolean`).
2. The relay (see `pi/relay`) is configured to subscribe to that node, so it will internally store the new value in its own `state` variable. 
   - 2a. If the Python Dashboard is active on a page that requires this data, it will send it through immediately via MQTT on the topic `relay/f/i/state/vgr`.
   - 2b. Otherwise, it waits to publish until the Python Dashboard publishes on `relay/read` with a payload like this:
```json
{
    "topics": ["relay/f/i/state/vgr"]
}
```
3. The Python Dashboard receives the message with its `MqttClient`, which is a singleton wrapper class for the standard `paho.mqtt.client` library class. The `WebSocketManager` class has a `request_handler` method that makes sure this message is sent through over a WebSocket to the frontend. The WebSocket path is `localhost:8765/relay/f/i/state/vgr`, if the WebSocket port is 8765. Note that this WebSocket path exactly mirrors the MQTT topic. 
4. On the frontend, there is a `Dash` `WebSocket` element (from `dash_extensions.WebSocket`). This WebSocket is created when the page loads and listens on this path. The `component_id` of this element is: `{"source": "mqtt", "topic": relay/f/i/state/vgr}`.
5. A `Dash` `callback` method uses the `component_id` in its `Input`, making sure that whenever the `WebSocket` element receives a message, it is reflected in the HTML layout. This is what the user sees.

For data sources other than the PLC, only steps 3 until 5 are applicable. Note that there will not be a `relay` part in the MQTT topic or WebSocket path in that case.

For sending data from the frontend to the PLC, it works simpler:

1. A Dash callback invokes `MqttClient.publish` to publish data on, say, `relay/f/o/state/ack`. It disables and greys out the button and adds the `pending` class to signify that there is a pending action for that button.
2. The relay is subscribed to this topic and stores the new data in its internal `state` variable. It sends the data to the PLC using OPC/UA over `ns=3;s="gtyp_Interface_Dashboard"."Publish"."ldt_AcknowledgeButton"`. 
3. It publishes a message to `relay/f/o/state/ack/response` like this: 
```json
{
    "message": "Sent value DataValue.Boolean: True to Node: ns=3;s=\"gtyp_Interface_Dashboard\".\"Publish\".\"ldt_AcknowledgeButton\""
}
```
4. On the frontend again, there is a Dash callback called `reset_acknowledge_button` that listens to `relay/f/o/state/ack/response` that will re-enable the button and logs the response message.