# MQTT Schema

MQTT, in this use case, is less "strict" than OPC/UA. It has two characteristics that cause this:
- Dynamic topic creation: When a client publishes to a topic that does not yet exist on the broker (the TXT controller, or `mosquitto` during dev/test), the broker automatically creates a new topic.
- Data format: In the ReMan use case, all payloads are free-form JSON strings. That means that sending two messages on the same topic with different data structures will be accepted, as long as they are valid JSON.

The schemas in this directory are there to document and give an overview of all used topics and what JSON data formats can be expected to be published on those routes.

## Topic Names

- `f`: "factory", topics pertaining to Fischer Factory function
- `c`: "config", configuration and status topics
- `i`: "in", topics that are published to by clients other than the Node-RED program (like the PTU, LDR etc)
- `fl`: !TODO: not sure what this is
- `f/i`: "in", topics that the Node-RED program publishes to to translate OPC/UA data from the PLC
- `f/o`: "out", topics that are published to from actions on the Node-RED Dashboard. The factory flows subscribe to this.

## Data Types

Since the messages are in JSON, the TypeScript primary types in the overview files correspond perfectly to the data types used in MQTT. One note should be made about the `Date` data type: it should be serialized to `<yyyy-mmddThh:mm:ss.fffZ>` format (which the standard `JSON.stringify` function should do be default).