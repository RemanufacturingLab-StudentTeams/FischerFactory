# Connect to Raspberry Pi 4 

## Monitor and keyboard
Either hook the monitor and keyboard to the Raspberry Pi
Login with username: `pi`, password: `pi`

## SSH
Ssh connection using ssh (Linux/Mac) or Putty (Windows):
### Putty
1. Download putty
1. Connect to `192.168.0.5` (IP address of Raspberry Pi)
1. login with username: `pi`, password: `pi`

### Linux/Mac
1. To connect 'ssh pi@192.168.0.5'
1. password: `pi`

## Tips for error analysis
1. Use the command `node-red-log` on raspberry pi
1. Log in on TXT-controller with ssh: `ssh ROBOPro@192.168.0.10` password: ROBOPro. Then connect to the screen session (screen is a terminal program that remote users can attach to to see the output of processes running within the screen shell). You can attach as follows:
  1.`screen -ls` # gives the screen-id, such as 1067.ROBOPRO
  1. `screen -x 1067.ROBOPRO` # attaches to the screen session in which the script run.sh is running, run.sh runs TxTControlMain.
  1. After use, first detach from the screen session with the key-combination Ctrl-a d (so first, `Ctrl-a`, then release all keys and then give `d`).
