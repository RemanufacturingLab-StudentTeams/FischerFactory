# Startup guide Fisher Factory
 
## Join the network of the Fischertechnik Factory:
Connect your Windows / Mac / Linux laptop to the WIFI network the Fischer Factory is connected to:
1. Now: TP-Link_EF41 (password: '69397301')
1.  In near future: iotroam

Currently, this is the Wifi network of the TP-Link router, the black one with the antennas near the FischerFactory (SSID, login and password are on the backside of the router).

 
## Startup procedure

1. When working with the Factory, remove the cover. If you are working the other day as well, no need to cover the Factory again, but over the weekend and holidays it needs to be covered to protect against dust and other harm.
  1. Make sure the RPi has an ethernet cable to the PLC switch (or to the router), and the PLC switch has an ethernet cable to the TP-Link wifi router (if the RPI has no network at boot, it will not get an IP address even after plugging the ethernet cable)
1. Make sure the small hardware switch on the PLC is in stop mode (middle position)
1. Powerup the Factory
  1. Connect the power plug
1. Turn on the TXT controller manually by pressing its on/off button for about a second or so
1. Wait until the LEDs on all the modules attached to the PLC are not flashing anymore and stay green, then switch the PLC from stop-mode to run-mode by the small hardware switch.
1. If the TXT controller is ready with its boot procedure, touch the touch screen to run the program.
 
Now you are ready to run the Factory with your internet browser. 
1. Note the node-red dashboard is at `192.168.0.5:1880/ui`(enter this in the address field of your browser).
1. If you want to monitor the node-red messages, the MQTT Explorer might be helpful. Connect to `192.168.0.5:1880`. No need to login with username / password.


## Closing down procedure

1. Turn off TXT controller with the power on/off button
1. Turn off RPi, by pressing the red button once (just switching off the power is not good for the state of the operating system and the condition of the SD card)
1. Turn PLC into stop-mode
1. Remove power plug

