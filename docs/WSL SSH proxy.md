# WSL SSH Proxy

The server runs a network proxy so that you can SSH directly into the WSL2 environment, instead of SSH-ing into Windows directly and then going into WSL, with all the security risks that could cause. The way it is set up right now involves a Startup Script called `proxy_setup` located in `C:\Users\reman\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`. This proxies port 2022 to port 2022 on WSL2, where an SSH agent is listening.

## Fix for not working

After a Windows update, this setup will not work. Restarting the "Ip Helper" service in the Windows Services tab, and/or manually running the `proxy_setup` script by double clicking seems to fix it.