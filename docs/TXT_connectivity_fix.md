## Steps to get connectivity over WiFi for the TXT Broker

1. Run a continuous pingtest on anther device on the `iotroam` network with `ping /t 10.35.4.253` on Windows CMD or `$ ping 10.35.4.253` on a Linux device.
2. On the touchscreen of the TXT, navigate to "Instellingen" > "Netwerk" > "WLAN Instellingen" > "WLAN Mode" > "WLAN Client Setup" > "IP" 
3. You should see two options in the middle of the screen now called "DHCP" and "Static". It should be set to "Static" by default. Change this to DHCP and press the red checkmark in the top-right of the screen to apply changes. 
4. Press the back-button in the top-left of the screen. 
5. Press the green checkmark on the top-right of the screen to restart the WLAN (WiFi) interface. Wait until the "Restart WLAN..." message disappears.
6. Navigate back to "WLAN Mode" > "WLAN Client Setup" > "IP".
7. Switch back to "Static".
8. Repeat step 4 and 5 to restart the WiFi again, this time in Static.

*Note: It might take around 30 seconds to a minute for connectivity to function again. When the continuous pingtest starts to succeed, that means it works.*

9. Press the back-button to get all the way back to the start menu and start the MQTT service.

*Note: MQTT Explorer is installed on the PC, this can be used to see if the MQTT service is working properly.*