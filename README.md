# Remanufacturing Lab - FischerFactory
This repository contains the custom code for the THUAS Remanufacturing Lab implementation and usage of the PLC, TXT controller/broker, and Node-RED flows of the FischerTechnik Lernfabrik. It also contains documentation for remote testing and development. Lastly, configuration for setting up Telegraf, InfluxDB and GraphDB and APIs is listed.

# General Overview
## File structure
This project consists of a number of (mostly) heterogeneous components, that are kept in separate project-level directories with their own documentation. These are:
- `pi`: Directory pertaining to the program(s) that run on the Fischer Factory Raspberry Pi. As of the time of writing, this is only the Node-RED program, which will probably be replaced with pure NodeJS in the future.
- `plc`: Contains development resources for the Fischer Factory PLC. The `PLC` subdirectory is used as a mount for the VCI addin for Tia Portal v17 and should preferably not be manually modified.
- `schemas`: Documentation and information models for all communication protocols used in the Fischer Factory.
- `server`: Development and administrative resources for the Fischer Factory part of the Central ReMan server. This includes InfluxDB/Telegraf, GraphDB and  AAS Basyx.
- `dashboard`: Remote dashboard for monitoring the pucks in the factory. Consumes data from the Central ReMan server.

## Testing

(Automated) testing is incredibly important, both for ensuring code correctness and to formally lay down expected behaviour. The different components have different testing requirements:
- `Node-RED`/`NodeJS` program: This is a proprietary (mostly self-coded) software, which means it is highly susceptible to bugs. 
- - Unit tests: At the time of writing, an automated test suite for unit tests does not yet exist. It should exist when developing the `NodeJS` replacement of the `Node-RED` program.
- - Integration testing: Both `Node-RED` and `NodeJS` can easily be ran in-situ or locally for testing. The `PLC` can be simulated using Siemens' PLCSIM v17 in Tia Portal's Simulation Mode. One can test that the correct MQTT messages are sent using the MQTT testing tool or with something like MQTT Explorer.

- `PLC` code: This codebase is tightly tied to the hardware, and unit tests are therefore not really possible. Integration tests can only be done in-situ.

- Central server: The programs running on the central server are non-proprietary, only the configuration files were written specifically for/by the ReMan Lab.
- - `telegraf`: Running unit tests against the configuration file is pretty much not possible, but integration tests can be done using the `server/mqtt_testing_tool` and by starting `telegraf` in "test" mode with `telegraf --test`.

### CI Pipeline
A CI Pipeline is a bit beyond the scope of this project, but it could still be added in the future.

## Local development

### Version control
A [Git Policy](docs/policy.md) was written for this project. Please adhere to it as tightly as possible during development.

### Documentation

Documentation requirements are different depending on the subject:
- Hardware: Please include a copy of any hardware manuals within the `docs` directory. 
- Non-proprietary software: A `README.md` file suffices. This file should explain the reason this software is used, how to set it up locally, and how to deploy it in production.
- Proprietary software and config files: A `README.md file` is necessary, and comments should be written within the code itself explaining what it is for.
- Schemas: These should be extensively documented. A comprehensive overview of the schema should be in the `schemas` directory, with a detailed `README.md`. The idea is that a collaborator should not have to be able to understand the internal workings of a component in order to still communicate with it over a given network protocol.

## Deployment

...

## Networking

All components are connected to the `iotroam` network (10.35.4.0/24) via an Archer C60 router running WDS to the gateway router. The IP addresses are statically assigned. They are as follows:

Device | IP Address
-|-
Archer C60 router | 10.35.4.250
ReMan Server | 10.35.4.251
PLC | 10.35.4.252
TXT Controller (broker) | 10.35.4.253
Raspberry Pi | 10.35.4.254

IP Addresses below 250 are dynamically assigned using DHCP, so it is not advisable when scaling the amount of devices up, to statically assign more addresses, as it could lead to conflicts with dynamically assigned addresses.

## Old Documentation
This project has been worked on for some years by many other people before, and they left reports and documentation on their work. They can be viewed in the Microsoft Teams Team for the ReMan Lab. 

*Note: Since their projects have finished, that documentation might be deprecated.*

# Attribution

- Project manager: [Dr. Rufus Fraanje](https://github.com/prfraanje)
- Collaborator - Server dev/admin: [Madeline Sebastian](https://github.com/blooburry)
- Collaborator: [Jip Rasenberg](https://github.com/Jipr)
- Collaborator (inactive): [Mariska van Beek](https://github.com/mariskavanbeek)
- Collaborator - PLC development: Yves Kersten
- Collaborator - Remote dashboard development: Antoine Dunand