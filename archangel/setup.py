import os
import shutil
import json

# install required pip packages
os.system('sudo pip install -r requirements.txt')
os.system('sudo pip3 install -r requirements.txt')

# currently only in ubuntu - install required packages:
packages = [
"sqlite3",
"nginx",
"python3-pip",
"git"
]

for p in packages:
    os.system(f'sudo apt-get install {p} -y')

os.system('sudo systemctl enable nginx')
os.system('sudo systemctl start nginx')

# setup archangel dir
if not os.path.isdir('/var/www'):
    os.mkdir('/var/www')
if os.path.isdir('/var/www/archangel'):
    if os.path.isfile('/var/www/archangel/config.json'):
        with open('/var/www/archangel/config.json', 'r') as f:
            old_config = json.load(f)
        with open('archangel/config.json', 'r') as f:
            new_config = json.load(f)
        for key in old_config:
            new_config[key] = old_config[key]
        with open('archangel/config.json', 'w') as f:
            json.dump(new_config, f, indent=2)
    if os.path.isfile('/var/www/archangel/db/accounts.db'):
        os.rename('/var/www/archangel/db/accounts.db', 'archangel/db/accounts.db')
    if os.path.isfile('/var/www/archangel/db/watch.db'):
        os.rename('/var/www/archangel/db/watch.db', 'archangel/db/watch.db')
    if os.path.isfile('/var/www/archangel/db/stream.db'):
        os.rename('/var/www/archangel/db/stream.db', 'archangel/db/stream.db')
    shutil.rmtree('/var/www/archangel')
    os.rename('archangel', '/var/www/archangel')
    print('Your Admin Login is still the same!')
else:
    os.rename('archangel', '/var/www/archangel')
    print('Login\nUsername: admin\nPassword: administrator01\n\nPlease change this as quick as possible!!!')
os.system('chown -R www-data:www-data /var/www')

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

# disable all other nginx sites
os.system('sudo rm /etc/nginx/sites-enabled/*')

# nginx config
if os.path.isfile('/etc/nginx/sites-available/archangel'):
    os.remove('/etc/nginx/sites-available/archangel')
    os.rename('sysfiles/archangel', '/etc/nginx/sites-available/archangel')
else:
    os.rename('sysfiles/archangel', '/etc/nginx/sites-available/archangel')
os.system('sudo ln -s /etc/nginx/sites-available/archangel /etc/nginx/sites-enabled')
os.system('sudo systemctl restart nginx')

