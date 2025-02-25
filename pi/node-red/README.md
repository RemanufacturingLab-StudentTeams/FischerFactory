# Node-RED

## General

The Fischertechnik Lernfabrik offers a collection of Node-RED flows, that have been modified to suit the purposes of the Remanufacturing Lab. They have three main functions:
-  Subscribing to the nodes that the PLC publishes on
- Creating a local Node-RED dashboard
- Translate the OPC/UA data to MQTT so the central ReMan server can consume the PLC data

*There are plans to move away from Node-RED and rewrite the code to NodeJS (the underlying technology of Node-RED). The flows are expected to move to legacy when that happens.*

## Deployment

### npm

First, install Node-RED:

```bash
$ sudo npm install -g --unsafe-perm node-red
```

Then start the Node-RED server using the `flows.json` file contained in this repo (after forking it to your machine):

```bash
$ node-red PATH/TO/FLOWS/flows.json
```

The server should be running on port 1880. Opening `localhost:1880` in the browser shows a GUI that can be used to change, start or stop the program. The dashboard can be accessed at `localhost:1880/ui`.

## Configuration

In the top right of the Node-RED GUI, clicking on the gear icon opens the config tab. There is only two config nodes that should be changed between dev and prod:
- A OPCUA-IIoT-Connector node with the name `SIEMENS PLC@10.35.4.252`, used to connect to the PLC
- and mqtt-broker node using MQTT V3.1.1

### Production
- PLC endpoint: `opc.tcp://10.35.4.252:4840`
- broker: `10.35.4.253:1883`

### Development

When developing locally, the IP addresses should be changed to `localhost`. Additionally, TIA portal can be used in Simulation mode to simulate the PLC (see `plc/README.md`), and `mosquitto` can be used to simulate the MQTT broker.

## Dependencies

- npm
- node-red v3.1.3
- node-red-contrib-iiot-opcua v4.1.2
- node-red-contrib-usbcamera v0.0.6
- node-red-dashboard v3.6.2
- node-red-base64 v0.3.0
- node-red-node-ui-table v0.4.3