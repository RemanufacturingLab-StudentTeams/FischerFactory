# OPC/UA Information Model

## Relation to the PLC DataTypes
For a comprehensive view of every datatype on the PLC, please consult @link "plc/PLC/PLC data types".
The PLC Data Types and the OPC UA nodes map to each other pretty much 1-to-1, with the nodeID of the
OPC UA Node being a concatenation of the DataType of all the ancestors and the type itself.

## General 
General information about the structure of the nodes:
- The nodes follow a hierarchical structure analogous to the DataTypes on the PLC.
- "Subscribe" nodes are for the Raspberry Pi to subscribe to. The PLC only publishes on these nodes.
- "Publish" nodes are the opposite: the Raspberry Pi publishes these, and the PLC consumes that data.
- The nodes are all in namespace 3.
## NodeID structure
The nodeIDs can be inferred from the Node structure. For instance, the node
`ns=3;s=V_"typ_MQTT_Interface_Dashboard_Subscribe"."State_VGR"."Workpiece"."Workpiece_States"."s_ObservedColor"`
has the following properties:
- Namespace 3, so `ns=3;`
- `V_` for UaVariable. `DT_` is for UADataType, and `VT_` for UAVariableType. So this node is a UAVariable definition.
  Most of the time, you want to subscribe to the actual instances of this variable, so omit the prefix entirely. (`s="gtyp_MQTT..."`)
- `typ_` shows again that this is a type definition. Use `gtyp` (global type) for instances instead.
- This node represents the `s_ObservedColor` field in the Workpiece_States type, in the Workpiece type, in the State_VGR type, etc.
- The `s_` prefix in the field name is for the built-in datatype:
  - `x_`: Boolean
  - `s_`: String
  - `w_`: Word
  - `ldt_`: DateTime
  - `i_`: Int16
  - `di_`: Int32 (di = double integer)
  - `r_`: Float (r = real)
  Some nodes do not have this prefix, which is why the datatype is explicitly listed in this document. 

Example of a node you might actually want to subcribe to:
`ns=3;s="gtyp_Interface_Dashboard"."Subscribe"."State_MPO"."x_active"`

## Files

- opcua_schema.ts

A comprehensive, human-readable, documented, (relatively) short overview of the OPC UA Nodes. Recommended first point of entry.

- opcua_schema.js

A non-comprehensive, documented list of nodeIDs, browseNames and DataTypes. Can be used for examples or reference when subscribing.

- nodeset.xml

A comprehensive view of every OPC UA Node can be found in "nodeset.xml". This file was sniffed during prod and contains the full NodeSet of the PLC and can be used in OPC UA simulation servers for remote development.
