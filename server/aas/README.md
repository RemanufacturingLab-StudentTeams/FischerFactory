# Basyx AAS

> Note: the ReMan use case still uses Basyx AAS v1. This is expected to change when we can figure out how to upgrade to v2 or v3.

The ReMan lab uses a number of OTS components from Eclipse Basyx to provide AAS functionality, as well as a proprietary program that acts as a supplement to the databridge. All of these can be started by simply running `docker compose build && docker compose run` (in this subdirectory).

## AAS Server

The AAS Server can be pulled from Dockerhub and used as an Off-The-Shelf component - the only configuration it needs is an .aasx file. This file can be created and viewed using [AasxPackageExplorer](https://github.com/eclipse-aaspe/aaspe). 

## Databridge

### Use case
In the FischerFactory, data is sent to the AAS server from the MQTT broker so it has a live representation of the data in the FischerFactory. This can then be queried or exposed with GUI via HTTP.

### Configuration
The configuration for the Databridge consists of routes. These routes consist of three parts: source, transformer(s), and sink(s). These are then put together in a [`routes.json`](https://wiki.eclipse.org/BaSyx_/_Documentation_/_Components_/_DataBridge_/_Features_/_Routes_Configuration). Each source, transformer and sink has an associated `uniqueId` property that can be used to reference it. Below is an example of how to use the Databridge for AAS/MQTT communication, from the [Basxy Databridge repository](https://github.com/eclipse-basyx/basyx-databridge/tree/main/databridge.examples/databridge.examples.mqtt-jsonata-aas).

### Example: MQTT -> AAS

#### Source
Example `mqtt_source.json` file:

```
[
	{
		"uniqueId": "temperatureSensor",
		"serverUrl": "host.docker.internal",
		"serverPort": 1884,
		"topic": "heater/temperature"
	}
]
```

#### Transformer
Example `jsonata_transformer.json` file:

```
[
    {
		"uniqueId": "temperatureTransformer",
		"queryPath": "temperatureTransformer.jsonata",
		"inputType": "JsonString",
		"outputType": "JsonString"
    }
]
```

The `queryPath` property contains a reference to the file with the mapping function `temperatureTransformer.jsonata`:
```
$floor((temperature - 32) * 5 / 9)
```

#### Sink

Example `aasserver_sink.json` file:
```
[
    {
		"uniqueId": "TemperatureSubmodel",
		"submodelEndpoint": "http://host.docker.internal:4001/aasServer/shells/heaterAAS/aas/submodels/temperatureSensor/submodel",
		"idShortPath": "currentTemperature"
    }
]
```

#### Putting it all together

Example `routes.json` file:
```
[
    {
		"datasource": "temperatureSensor",
		"transformers": ["temperatureTransformer"],
		"datasinks": ["TemperatureSubmodel"],
		"trigger": "event"
	}
]
```

## AAS Registry

The OTS component for the registry (the component that holds all the shells) is pulled off of Dockerhub and used as-is. 

## AAS GUI

This is the OTS component that allows users to view the AAS' in a graphic way. It can be accessed at `localhost:3000`.