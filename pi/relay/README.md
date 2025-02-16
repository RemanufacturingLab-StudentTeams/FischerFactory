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

## General Architecture and Design

*This is only a high-level overview of the general design of the program. Each individual class also contains documentation in the form of PyDoc.*

### Concurrent design

The two functions (relaying MQTT->OPCUA and OPCUA->MQTT) of the relay should run concurrently, and because of this the functions that perform these things are `async` using `asyncio.gather`. There is also another function called `listen_for_read_requests`, which is elaborated on in the `State` section.

### Configurability

Using the `mappings.py` file, which topics will be mapped to which nodes and vice versa can be exactly specified.

#### Special rules

Some MQTT topics in the original Node-RED dashboard do not follow the OPC-UA structure at all (e.g. `State_SLD` in the MQTT schema is `state/sld`, notice that the MQTT topic has an extra level of nesting). There are also OPC-UA nodes that themselves don't even follow the OPC-UA naming convention because they were added by the ReMan lab student teams, not FischerTechnik (e.g. `DoOven`, which by FischerTechnik naming convention should be `x_doOven`, the `x_` prefix indicating a boolean type). For these cases, the `mappings.py` file can contain "special rules" so the relay will interpret the node ID parts given by `ORIGINAL` as the value given by `MEANS` when converting the names to MQTT.

### Helper functions

1. `name_to_mqtt`: Because the naming conventions for MQTT and OPCUA are different, the names of the subnodes cannot be used as they are. For instance, `EnvironmentSensor.ldt_ts` should become `environmentSensor.ts` to fit the MQTT naming conventions. Furthermore, this function should respect the special rules from the mappings file.
2. `get_datatype_as_str` retrieves the datatype identifier from the server and maps this to the human-readable datatype as a string. It can also detect Array types and non-primitive (Nested) types. This function is necessary for the `value_to_ua` function to work properly.
3. `value_to_ua`: Converts a Python value to the corresponding OPCUA value from `asycua.ua`. Technically, the library does this automatically, but doing it like this gives more control over the process. 

### MQTT -> OPCUA

To translate MQTT messages to OPCUA, a custom MQTTClient wrapper class is used. This class provides a subscribe method that takes a callback, which will be called whenever the client receives a message on the topic. This callback should do the following:

1. Check if the value is:
- - A single value: This means the value is for an *independent field* node. The value is converted to the OPCUA equivalent.
- - A nested value: This means the value is for a normal leaf node (leaf nodes take a `dict` payload). 
- - 1. The `get_targets_and_values_for_node` function aims to find all the relevant field nodes that should receive their corresponding parts of the payload (e.g., `..."EnvironmentSensor"."ldt_ts"`, `..."EnvironmentSensor".r_t`, `..."EnvironmentSensor".r_rt` etc). 
- - 2. Using the `get_children` the first-level field nodes are found. 
- - 3. If the datatype of the field is a primitive, the node and the corresponding value are added to the `targets` and `values` variables. These will be used in the `opcua_client.write_values` function to send the values to the nodes in one call. 
- - 4. Otherwise, the payload is double-nested, and the function will recurse on the field node, finding the field nodes of the field node. 
2. The value is sent to the PLC. The result is awaited.
3. If it succeeds, a response over MQTT is sent back over the `/ack` subtopic of the original topic with a `msg` field in the payload. Otherwise it will have an `err` field instead. 

### State

MQTT is a stateless protocol. This means that it does not inherently remember what the value of a topic was: when it's been sent, it's gone, and another client cannot retrieve the value at a later date - they had to be subscribed at that moment. Unfortunately the Python dashboard in particular does require a state. Imagine for instance a node like "State_Order", which is used to communicate the status of a puck order (`IN_PROCESS`, `WAITING_FOR_ORDER`, etc.) If the user on the dashboard is on the homepage, instead of the `customer_dashboard` page, the Python dashboard will not be subscribed to the corresponding MQTT topic (and even if it was, the page would be re-rendered on load so the data would be lost), so when the user switches to the `customer_dashboard` page, they will have completely missed any previous updates, and the field will remain empty until a new value is emitted on the topic.

To remedy this, the relay maintains a `state` (i.e., a variable that remembers the last emitted value on each OPCUA node). Thus, when a page loads, the Python dashboard can request that the last remembered value from the state is re-emitted. This state is structured in exactly the same way that the MQTT schema is. 

The `listen_for_read_requests` function exists for this purpose. It checks the `relay/read` topic for such requests and re-emits for all the topics specified in the array `topics` field in the payload.

### OPCUA -> MQTT

Because the OPCUA->MQTT relay is recursive on the source node (i.e., it will browse the child nodes of the source node and relay it all the way down), it is notably more complicated than the reverse. In general:

1. It checks the mappings file to see which node to relay. This node become the `root_node` and is mapped to the `base_topic`. 
2. It browses the children of the `root_node` to discern if it is a *non-leaf*, a *leaf*, or an *independent field*. 
- 1. If it is a non-leaf, it will recurse, using the child node as the new root node and taking the `EXCLUDE` option in mind. It will generate the subtopic name using the helper function `name_to_mqtt`.
- 2. If it is a leaf, it means the children should be parsed as a payload. The `LeafDataChangeHandler` class is used to subscribe to the node. This handler will update the `state` and send the new value over MQTT. When the subscription is made, the initial value is read automatically and sent over MQTT. 
- 3. If it is a leaf, but it cannot be subscribed to, it means *its* children are independent nodes. The `FieldDataChangeHandler` class is used to subscribe to these nodes one by one. 

The rest of the logic for parsing the OPCUA values and sending them to MQTT is abstracted away using the DataChangeHandler classes.
