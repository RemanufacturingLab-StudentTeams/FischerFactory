# Raspberry Pi Python Program

This program is meant to replace the old Node-RED program and Dashboard.

## Dependencies

The dependencies are given in the Pipfile (and corresponding lockfile). This project uses pipenv to manage them.

### Schema files

It depends on the schemas/mqtt/mqtt_schema.ts file being present and correct, as it uses this file to know which topics exist and it can subscribe to. When changing this file, reflect the change in this program.