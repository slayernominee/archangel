# Arch Angel
A Platform where you can set up streaming links for e.g YouTube vivo etc
You can stream the links that were setup most times directly on Arch Angel
There are Search Index Admin Settings User Profiles Spotlights Account Settings
User Mangagment 2FA for Login settings for public viewing, registering etc
It's a lot customizable.

<img style="width: 600px; height: 300px;" src="https://cdn.discordapp.com/attachments/801551579455029299/964096077194207262/unknown.png?size=4096">
<img style="width: 600px; height: 300px;" src="https://cdn.discordapp.com/attachments/801551579455029299/957640743915253791/unknown.png?size=4096">
<img style="width: 600px; height: 300px;" src="https://cdn.discordapp.com/attachments/801551579455029299/954049659423318016/unknown.png?size=4096">

## Requirements
- Python3
- Git
- Apt Package Manager
- Pip Installed
## Installation
`git clone https://github.com/slayernominee/archangel.git && cd archangel && cd archangel`

`sudo python3 setup.py`

### Info
-> The Installer will setup a Nginx Server and a Flask Systemd Process
-> The Flask Process (archangel) will be displayed on Port 80 (http) on the Flask Server
-> The Flask Server is just a reverse proxy
### Additional
-> If you want to use https, just install certbot
-> Check that your domain records are correct (a -> ipv4, aaaa -> ipv6)
-> Run `sudo certbot -nginx` and follow the wizard, this should create the matching configuration
-> Test it by using `https://<yourdomain>/home`
