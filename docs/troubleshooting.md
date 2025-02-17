# Troubleshooting

Sometimes things in the factory just do not work. For instance, you order and nothing happens, or you place a puck in input and it just won't accept it or the VGR does not do anything at all.

## Power cycle

Turn it off and on ¯\\\_(ツ)_/¯

## Network

Most of the time the problem is the network connectivity which is rather unreliable, mostly because of the TXT broker and its reliance on WiFi. Open MQTT Explorer on the server to check if it can connect, and `ssh` into the Raspberry Pi as well to ping the TXT broker:

```bash
> ssh pi@10.35.4.254 (enter password for the RPi when prompted)
$ ping 10.35.4.253 (TXT broker address)
```

If this is the problem, following the [connectivity fix.](./TXT_connectivity_fix.md).

## Dashboard

What also often happens is that it is a software error (and/or a bug) in the Python dashboard. It was developed by a single individual after all. Please monitor the Log on the dashboard itself for any warnings or errors that might explain the issue. Also, when interacting with the buttons on the dashboard, please wait until they stop flashing. The PLC might be slow, so this could take a while - give it a minute or two at least. Lastly, MQTT Explorer can also be used to monitor the input to the dashboard.

## TXT Broker

Sometimes the ROBOPro program on the TXT broker is not running. SSH into it and use `screen` to attach to the ROBOPro screen to monitor it:

```bash
> ssh ROBOPro@10.35.4.253 (enter password when prompted)
$ screen -ls (to obtain the screen id of "ROBOPRO")
$ screen -d -r 985 (or whatever the id is)
```

The source code of this program is available online in the [FischerTechnik repository](https://github.com/fischertechnik/txt_training_factory/blob/master/TxtFactoryMain/src/main.cpp).

## PLC

Sometimes the PLC is the problem. If any of the stations throw an error, it should be shown on the dashboard, and they can be reset using the "ACK" button on the overview page of the dashboard. And even if the error message does not show up, hitting this button doesn't do any harm. 

The PLC might also be overloaded. Using TIA Portal v17 (already installed on the server), you can view the "Online and diagnostics" of the PLC. Note the "Cycle time" and "Work memory". These should stay under 50ms and 40% respectively during normal usage.

## Physical

Sometimes a cable is loose. This happened with the camera station (SSC) a few times and also with the TXT. Giving them a bit of a tug or turning them a bit works sometimes.

Also sometimes the PLC isn't plugged into power (stupid, I know, but it happened more than once). 