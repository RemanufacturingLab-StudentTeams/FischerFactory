# InfluxDB

The RemanLab uses InfluxDB to store a history of the states of the different Fischer Factory components. These measurements are then placed in the `FischerFactory` bucket.

## Local Setup
Firstly, you have to install InfluxDB v2 (OSS), and the Influx CLI. [Here is the link to the official guide](https://docs.influxdata.com/influxdb/v2/install/?t=Linux).

When authenticating, you might need these:

Authentication field | Value
-|-
Host URL | localhost:8086
Organization Name | Remanufacturing Lab
Organization ID | 80627e52d150f118
Token | ****

Then, make sure to install Telegraf as well.

## InfluxDB

Simply start the database with `$ influxd` after completing the setup. You should be able to open a GUI at `localhost:8086` to query the data locally, and a HTTP API should be exposed to query it with Flux as well (see `schemas/http`).

## Telegraf
For the ReMan use case, Telegraf is configured to consume MQTT data from the broker. See `telegraf.dev.conf` for an example of a local configuration file (the production configuration file is secret). It subscribes to the following topics:

- f/i/state/#

The datapoints that it then outputs to InfluxDB mirror the JSON formats of those messages exactly, so `schemas/mqtt` can be consulted to see what the measurements look like.

*Note:*

For now, Telegraf creates one client for each topic, because each input plugin needs a different JSON parser (because the topics do not have the same payloads). This is quite inefficient in terms of connections, and it is possible to have one client subscribe to multiple topics - this is also done with DSI/DSO. However, at the time of writing, I have not yet found a way to ascribe different parsers for the same plugin. 

### Usage
Telegraf, after being installed, can be started with `$ telegraf --config PATH/TO/CONFIG/telegraf.dev.conf`. If you want to test the MQTT consumer functionality, you must also start a broker and the Node-RED program / the MQTT testing tool.