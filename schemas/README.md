# Schemas

For communication 

## MQTT
MQTT is the protocol used to communicate between:
- The Node-RED program and itself (to communicate between the Factory flows and the Node-RED Dashboard flow)
- The Node-RED program and the Central ReMan sever
- Miscellaneous factory components and the Node-RED program (like the LDR and PTU)

*Note: in the future, Node-RED might deprecate in favour of NodeJS, but the MQTT schema will stay the same if that happens.*

## OPC/UA
OPC/UA is the protocol used for communication between the PLC and the Node-RED program. It is highly structured, for more information about this structure please consult `opcua/README.md`. 

## HTTP/REST
The InfluxDB and GraphDB databases on the Central ReMan server expose their data with a HTTP/Rest API for Flux and SPARQL respectively. See `http/README.md` for more information.
