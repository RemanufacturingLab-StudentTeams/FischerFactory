## Startup procedure

0) When working with the Factory, remove the cover. If you are working the other day as well, no need to cover the Factory again, but over the weekend and in holidays it need to be convered to protect against dust and other harms.
Make sure the RPi has an ethernet cable to the PLC switch (or to the router), and the PLC switch has a ethernet cable to the TP Link wifi router (if the RPI has no network at boot, it will not get an IP address even after plugging the ethernet cable)
1) Make sure the small hardware switch on the PLC is in stop mode (middle position)
2) Powerup the Factory
3) Turn on the TXT controller manually by pressing its on/off button about a second or so
4) Wait until the LED's on all the modules attached to the PLC are not flashing anymore and stay green, then switch the PLC from stop-mode to run-mode by the small hardware switch.
5) If the TXT controller is ready with its boot procedure, touch the touch screen to run the program.
 
*Note: Very often, the TXT broker does not initially connect. See the [documentation](./TXT_connectivity_fix.md) on how to fix this.*

Now you are ready to run the Factory. Note the node-red dashboard is at 192.168.0.5:1880/ui
If you want to monitor the node-red messages, the MQTT Explorer might be helpful. Connect to 192.168.0.5:1880. No need to login with username / password.
 
## Closing down

1) Turn of TXT controller
2) Turn of RPi, e.g. with procedure written above
3) Turn PLC into stop-mode
4) Remove power plug