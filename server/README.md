# Remanufacturing Lab Central Server

This subdirectory contains all the configuration and source code files for the Central Server of the ReMan lab. The server is responsible for persisting factory data of the various components, and for exposing said data in the form of dashboards, database GUIs, and the AAS' (Asset Administration Shells).

## InfluxDB

This is the main database that, at the time of writing, persists data from the FischerFactory. It depends on the PLC and the MQTT broker / TXT controller of the FischerFactory to do so. See [the documentation for our use case of InfluxDB and Telegraf](./influx/README.md) for more information. The Dash dashboard, made by Antoine Dunand, depends on this database to be up and running to work.

## Basyx (AAS)

## GraphDB

> Not implemented yet at the time of writing.

## Basyx (AAS)

The ReMan server maintains a number of AAS components and proprietary programs, bundled together using Docker Compose. See the [documentation for our use case of Basyx AAS](./aas/README.md) for more information.
