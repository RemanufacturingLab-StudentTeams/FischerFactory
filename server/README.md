# Remanufacturing Lab Central Server

This subdirectory contains all the configuration and source code files for the Central Server of the ReMan lab. The server is responsible for persisting factory data of the various components, and for exposing said data in the form of dashboards, database GUIs, and the AAS' (Asset Administration Shells).

## InfluxDB

This is the main database that, at the time of writing, persists data from the FischerFactory. It depends on the PLC and the MQTT broker / TXT controller of the FischerFactory to do so. See [the documentation for our use case of InfluxDB and Telegraf](./influx/README.md) for more information. The Dash dashboard, made by Antoine Dunand, depends on this database to be up and running to work.

## Basyx (AAS)

## GraphDB

> Not implemented yet at the time of writing.

## Basyx (AAS)

The ReMan server maintains a number of AAS components and proprietary programs, bundled together using Docker Compose. See the [documentation for our use case of Basyx AAS](./aas/README.md) for more information.

## SSH Connection to ReMan Server

SSH allows you to connect your local device to the ReMan server.

**Prerequisites:**

* A user account must be created on the ReMan server.

**User Account Creation Steps:**

1.  Add the local device's MAC address to the server's access list.
2.  Add the user account to the `iotroam` network.
3.  Add the user account to the ReMan server itself.
4.  Ensure your local device is connected to the `iotroam` network.

**Connection Methods:**

### Connecting via Command Prompt (CMD)

1.  Open Command Prompt (CMD).
2.  Execute the following command: `ssh reman@10.35.4.251`
    * Replace `reman` with the actual username if needed.
    * If needed add `-p xxxx` with the correct port number. 
3.  Enter the user's password when prompted.
4.  Once connected, you will be in the server's shell (typically `bash`).

### Connecting via Visual Studio Code (VS Code)

1.  Install the "Remote - SSH" extension in VS Code.
2.  Open the command palette (Ctrl+Shift+P or Cmd+Shift+P) and type "Remote-SSH: Connect to Host".
3.  Select "Add New SSH Host..." and then enter the following SSH connection string: `ssh reman@10.35.4.251 -p xxxx`
    * Replace `reman` with the actual username.
    * Replace `10.35.4.251` with the server's IP address if different.
    * Replace `xxxx` with the correct port number.
4.  Select the platform type as "Linux".
5.  Enter the user's password when prompted.
6.  VS Code will establish the SSH connection and open a remote window.

**Troubleshooting:**

If you are unable to connect to the server, check the following:

1.  **Server Status:** Verify that the ReMan server PC is running.
2.  **Network Connectivity:** Confirm that both your local device and the server are connected to the `iotroam` network.
3.  **Ping Test:** Attempt to ping the server's IP address: `ping 10.35.4.251`
    * If you do not receive a response, there may be a network connectivity issue.
4.  **IP Helper Service (Windows):** If you receive ping responses but still cannot connect, try restarting the IP Helper service on the ReMan server:
    * Open the Windows Services application (search for "services").
    * Locate the "IP Helper" service.
    * Right-click and select "Restart".