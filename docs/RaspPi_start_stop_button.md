# Pi start-stop button
GitHub repository used: 'https://github.com/Howchoo/pi-power-button'

Youtube: 'https://www.youtube.com/watch?v=wVnMZ4DXDNo&t=595s&ab_channel=Howchoo'

## Functionalities 

1. **Shutdown functionality:** Shut the Pi down safely when the button is pressed. The Pi now consumes zero power.
1. **Wake functionality:** Turn the Pi back on when the button is pressed again.

## Hardware
1. Normally open (NO) power button, some jumper wires
1. Connect the power button to Pin 5 (GPIO 3/SCL) and Pin 6 (GND)
  1. For Rasp Pi 4 b  (current one FisherFactory) Pin 5 (GPIO 9/SCL) and Pin 6 (GND) works with following script

## Install
1. Connect to Rasp Pi with SSH
1. Download Git if necessary 'sudo apt-get install git'
1. Clone GitHub repository `git clone https://github.com/Howchoo/pi-power-button.git`
1. Run the setup script: `./pi-power-button/script/install`
1. Now the start-stop button should work

## Uninstallation
If you need to uninstall the power button script in order to use GPIO3 for another project or something:

1. Run the uninstall script: `./pi-power-button/script/uninstall`

## Status indicator LED Raspberry Pi
Used link: https://howchoo.com/pi/build-a-simple-raspberry-pi-led-power-status-indicator/
To indicate if the Pi is running or not, a LED is added. The green LED turns on when the Pi is completely running (not booting). And it will turn off when the Pi is completely inactive. 
### Hardware
1. Green LED 2.2V
1. Resistor 100Ω connected to the positive 
1. Connect the positive of the LED to the TxD pin (GPIO 14)
1. Connect the negative of the LED to the ground

### Software
1. Connect to Rasp Pi and open config.txt `suda nano /boot/config.txt`
1. Add the following line: `enable_uart=1`
1. Reboot the Pi 'sudo reboot'
