# MQTT Testing Tool
This tool was created in Rust to send test values on known topics to a local MQTT broker on `localhost:1883`. It also prints all received values to `stdout`.

## Usage
First, make sure a local MQTT broker is running (e.g. `mosquitto`) on `localhost:1883`. Then run the program using `$ cargo run` within the `mqtt_testing_tool` directory.