# MQTT Testing Tool
This tool was created in Rust to send test values on known topics to a local MQTT broker on `localhost:1883`. It also prints all received values to `stdout`.

## Usage
If in dev mode: First, make sure a local MQTT broker is running (e.g. `mosquitto`) on `localhost:1883`. Then run the program using `$ cargo run` within the `mqtt_testing_tool` directory. By default, it runs in dev mode. 

Use `$ cargo run -- prod` to run it for production mode. In this case, it expects a broker on `10.35.4.253:1883`.