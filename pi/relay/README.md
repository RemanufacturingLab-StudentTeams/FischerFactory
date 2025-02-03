# OPCUA-MQTT Relay

A simple program that relays messages from OPC UA to MQTT, and vice versa. Reads from the file mappings.py to know which nodes it should map to which topics.

## Requirements

- Linux Bash
- Python 3.12.8
- Pip 24.3.1
- Pipenv 2024.4.0

Further requirements are found in the `Pipenv` file. These can be automatically installed if the requirements above are provided. 

## Configuration

The relay contains a file `pi/relay/mappings.py`. This file determines which MQTT topics will be mapped to which OPC/UA nodes, and which nodes will be mapped to which MQTT topics (separate configuration, mapping is not automatically two-way). The configuration for this is done directly in Python, so installing a Python linter or analyzer could be useful to ensure good syntax. More documentation in the file itself.

### Environment variables

The program also uses a `.env` file. These values are required to be in there:

|Key|Example Value|Explanation
|-|-|-|
PLC_IP|10.35.4.252 | IP address of the PLC, see the `Networking` section in the top-level README
PLC_PORT|4840 | PLC OPC/UA port
MQTT_BROKER_IP|10.35.4.253 | IP address of the TXT broker
MQTT_BROKER_PORT|1883 | Port of the TXT broker
MQTT_USERNAME|relay | Username the relay uses for the MQTT connection with the broker
MQTT_PASSWORD|relay | Password the relay uses for the MQTT connection with the broker
LOG_LEVEL | DEBUG | Can be set to DEBUG, INFO, ERROR, CRITICAL. 

## Running the program

The program should be run with `pipenv`. Simply perform `pipenv run python main.py` in the relay directory for it to run.

When first running it, there will be a lot of yellow (warning) log messages talking about Subscriptions. This is normal and it means the relay is still establishing the OPC/UA Subscriptions to the PLC. During this time, the dashboard will not function properly. This process usually lasts less than a minute, before the yellow disappears and mostly white (DEBUG) and blue (INFO) log messages are shown. 

## Features

### Recursive subscriptions

When adding an OPC/UA -> MQTT mapping, the relay will automatically browse all the child nodes of the requested source OPC/UA node and map them to MQTT topics, preserving the structure of the OPC/UA nodes.

### Volatile Internal State 

The relay remembers the most recent emitted value for every MQTT topic for the duration that it is active. It does this using its internal `state` variable. When it is stopped and restarted, it populates this variable again.

When a MQTT message is published to `relay/read` with this structure:

```json
{
    "topics": ["topicA", "topicB"] 
}
```

it will re-publish the last published value for topics `topicA` and `topicB` that it remembered. This is used in the Dash program for when a page loads.

### Acknowledgements and Error Handling

When a message is published on a relay topic that is mapped to an OPC/UA node, it will publish an acknowledgement message when it has done so. This message is published to `<original_topic>/response`, and has this format:

```json
{
    "msg": "some_message",
    "err": "some_error",
}
```

It send either a `msg` or an `err` field (if the operation failed), not both.

### OPC/UA Subscription Cap Workaround

The PLC's OPC/UA server has a set maximum on the amount of Subscriptions a client can make. This limits the amount of mappings that can exist. A workaround for this has been implemented: the relay simply creates a new client every time this happens. That is why in the code, `opcua_clients` is a `list[OPCUAClient]`, as opposed to `mqtt_client` which is a singular `MQTTClient`.

## Special terms used in the code and comments

In the code, terms like "leaf node", "field node" and "independent (field)" node get used with some regularity. These terms refer to how OPC/UA nodes are mapped to MQTT topics:

1. A leaf node is a node that has at least one child that has no children of its own. Leaf nodes are always directly (non-recursively) mapped to MQTT topics. For example, `ns=3;s="Queue"` is a leaf node, because its values have this format:
```ts
{
    x_Queue_Full: DataType.Boolean
    i_Queue_Index: DataType.Int16
    Queue: FixedLengthArray<{
        ldt_ts: DataType.DateTime
        s_type: 'RED' | 'WHITE' | 'BLUE'
        Workpiece_Parameters: typ_Workpiece_Parameters
    }, 7>
}
```
It is a rather complicated payload, but nonetheless, the `x_Queue_Full` child node and the `i_Queue_Index` child node have no children, therefore it is a leaf node. It is directly mapped to `f/queue` without being recursed.


2. A field node is a node with no children. That is, it has a primary value (like a Boolean or a Int16). It is not mapped to an MQTT topic, but it is part of the payload that is. For instance, `x_Queue_Full` in the example above is not mapped to any topic directly, but is sent to `f/queue` as part of a payload.

3. An independent node is a field node who's parent node is not a `UAVariable` type. What that means is that the parent (leaf) node cannot be subscribed to, because its children (fields) can change independently from each other, resulting in a partial change to the payload (instead of every field in a payload changing at the same time, which is what usually happens). For instance, in `ns=3;s="gtyp_Setup"`, its field nodes can change without the other ones changing, meaning the code is different because the parent node cannot be subscribed to. The relay has implemented functionality to group these independent nodes together and re-emit the entire payload (including the rest, which have not changed since last time) when this happens. 
