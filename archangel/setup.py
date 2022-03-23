import os
import shutil
import json

# Install required pip packages
os.system('sudo pip install -r requirements.txt')
os.system('sudo pip3 install -r requirements.txt')

packages = [
"sqlite3",
"nginx",
"python3-pip",
"git"
]

# System Updaten
os.system('sudo apt-get update')

# Install required packages
for p in packages:
    os.system(f'sudo apt-get install {p} -y')

# Nginx starten
os.system('sudo systemctl enable nginx')
os.system('sudo systemctl start nginx')

# Create Path if it doesnt exists
if not os.path.isdir('/var/www'):
    os.mkdir('/var/www')

if os.path.isdir('/var/www/archangel'):
    # Save Config Rules that exists
    if os.path.isfile('/var/www/archangel/config.json'):
        with open('/var/www/archangel/config.json', 'r') as f:
            old_config = json.load(f)
        with open('archangel/config.json', 'r') as f:
            new_config = json.load(f)
        for key in old_config:
            new_config[key] = old_config[key]
        with open('archangel/config.json', 'w') as f:
            json.dump(new_config, f, indent=2)
    # Save Language Replacements Rules that exists
    if os.path.isfile('/var/www/archangel/languagereplacements.json'):
        with open('/var/www/archangel/languagereplacements.json', 'r') as f:
            old_config = json.load(f)
        with open('archangel/languagereplacements.json', 'r') as f:
            new_config = json.load(f)
        for key in old_config:
            new_config[key] = old_config[key]
        with open('archangel/languagereplacements.json', 'w') as f:
            json.dump(new_config, f, indent=2)
    # Save DB's if they exists
    if os.path.isfile('/var/www/archangel/db/accounts.db'):
        os.rename('/var/www/archangel/db/accounts.db', 'archangel/db/accounts.db')
    if os.path.isfile('/var/www/archangel/db/watch.db'):
        os.rename('/var/www/archangel/db/watch.db', 'archangel/db/watch.db')
    if os.path.isfile('/var/www/archangel/db/stream.db'):
        os.rename('/var/www/archangel/db/stream.db', 'archangel/db/stream.db')
    if os.path.isfile('/var/www/archangel/db/notifications.db'):
        os.rename('/var/www/archangel/db/notifications.db', 'archangel/db/notifications.db')
    if os.path.isfile('/var/www/archangel/db/calendar.db'):
        os.rename('/var/www/archangel/db/calendar.db', 'archangel/db/calendar.db')
    # Clear Complete Archangel Dir
    shutil.rmtree('/var/www/archangel')
    # Copy new Archangel Dir
    os.rename('archangel', '/var/www/archangel')
    print('Your Admin Login is still the same!')
else:
    # Create Archangel Dir
    os.rename('archangel', '/var/www/archangel')
    print('Login\nUsername: admin\nPassword: administrator01\n\nPlease change this as quick as possible!!!')
# Set Permissions for Archangel Dir
os.system('chown -R www-data:www-data /var/www')

# Start / Restart & Update Archangel Service
if os.path.isfile('/etc/systemd/system/archangel.service'):
    os.system('sudo systemctl disable archangel')
    os.system('sudo systemctl stop archangel')
    os.remove('/etc/systemd/system/archangel.service')
    os.rename('sysfiles/archangel.service', '/etc/systemd/system/archangel.service')
    os.system('sudo systemctl daemon-reload')
else:
    os.rename('sysfiles/archangel.service', '/etc/systemd/system/archangel.service')
    os.system('sudo systemctl daemon-reload')
os.system('sudo systemctl enable archangel')
os.system('sudo systemctl start archangel')

# Create Nginx Config if it doesnt exists
if not os.path.isfile('/etc/nginx/sites-available/archangel'):
    # Disable all Nginx Pages
    os.system('sudo rm /etc/nginx/sites-enabled/*')

    # Update / Set Up the Archangel Config
    if os.path.isfile('/etc/nginx/sites-available/archangel'):
        os.remove('/etc/nginx/sites-available/archangel')
        os.rename('sysfiles/archangel', '/etc/nginx/sites-available/archangel')
    else:
        os.rename('sysfiles/archangel', '/etc/nginx/sites-available/archangel')
    
    # Enable the Config
    os.system('sudo ln -s /etc/nginx/sites-available/archangel /etc/nginx/sites-enabled')
    # Restart the Nginx Service
    os.system('sudo systemctl restart nginx')

# Notice for HTTPS
print('''
# HTTPS Setup
  If you currently dont run you Archangel Application over https
  consider to enable https, it will increase the security of your
  site and also improve the user expierience
## Requirements
- You need to have a static ip adress
## Setup
- Setup in your Domain Settings the A & AAAA records to your server ipv4 & ipv6
- Run on the server   sudo certbot --nginx   and follow the wizard
''')