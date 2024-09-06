# Puck Tracker

This is a small Rust program that subscribes to the MQTT broker to keep track of whenever an order is placed and what colour puck it is for. Then, when a message is sent over `f/tracking`, it can deduce which puck caused that message to be sent. 

Finally, it sends a message on one of the `aas/#` topics (for instance, `aas/mpo`) to tell the AAS server how many red, blue and white pucks currently reside in each factory component.

## Dependencies

- `cargo`
- The MQTT broker
- The AAS server, registry, and databridge, connected to the MQTT broker
- Someone to sends order and tracking messages for the program to track. This can either be the Node-RED/NodeJS program, or the mqtt testing tool.

> Note: Since this program resides between the AAS and the broker, it could also be used to translate MQTT to HTTP, which would render the databridge unnecessary. However, at the time of writing, the extra scope the Tracker Program would be responsible for was deemed not worth it.