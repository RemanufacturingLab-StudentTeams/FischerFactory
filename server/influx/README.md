# InfluxDB

The RemanLab uses InfluxDB to store a history of the states of the different Fischer Factory components. These measurements are then placed in the `FischerFactory` bucket.

## Prod Setup

> Note: the configuration files for production (telegraf.prod.conf and optionally influxdb.prod.conf) are not tracked by version control, because they contain sensitive information - however, they should be present on the server locally. If that is not the case (which probably means something is seriously wrong), the dev files can be copied and renamed (e.g., telegraf.dev.conf -> telegraf.prod.conf) to be used during production.

Some parts of the production setup have been automised using Docker and Bash. Here are the steps to get the Influx + Telegraf setup running:

1. Run `auth-setup.sh`. Make sure to provide the password and authentication token as command line arguments. You might need to make the file executable if that hasn't been done yet. Example:

```bash
Make the file executable: 
$ chmod +x auth-setup.sh
Run it (in production mode): 
$ ./auth-setup.sh -e prod -p "example_password" -t "example_token"
```

> **IMPORTANT!** Remember to change the password and token back to their placeholder values in the compose.yaml and telegraf.prod.conf after usage if you want to push to the GitHub! The token and password are NOT allowed to get into the repository!

2. Use Docker Compose to run the Telegraf and Influx containers:

```bash
$ docker compose build && docker compose up
```

After you are done, you can use `$ docker compose down` to stop the containers.

## Local (Dev) Setup

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

The same steps used for production (the auth script and the Docker Compose setup) can also be used for development. The only difference is that the `-e` argument for the bash script should be given the value "dev" instead of "prod" when running it.