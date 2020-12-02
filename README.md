# peach-vps

![Generic badge](https://img.shields.io/badge/version-0.2.0-<COLOR>.svg)

Scripts for configuring the PeachCloud VPS for various hosting and automation functions.

Currently:
- Debian repository of microservices

# Setup Debian repo

An idempotent script for initializing the Debian repo on the VPS

```
sudo apt update
sudo apt install git python python3-pip rsync
git clone https://github.com/peachcloud/peach-vps.git
cd peach-vps
pip3 install -r requirements.txt
# open scripts/setup_debian_repo.py and set the following constants:
# USER_PATH, GPG_KEY_EMAIL, GPG_KEY_PASS_FILE
python3 scripts/setup_debian_repo.py -i
```

# Update Debian repo

Without the -i flag, the `setup_debian_repo` script rebuilds all
microservices (cross-compiled to arm64) and updates the Debian repo

```
cd peach-vps
python3 scripts/setup_debian_repo.py
```

# Using the Debian repo

To add the PeachCloud Debian repo as an apt source, run the following commands from your Pi:

```
vi /etc/apt/sources.list.d/peach.list
```

and add the following line:

```
deb http://apt.peachcloud.org/debian/ buster main
```

Then add the gpg pub key to the apt-key list:

```
wget -O - http://apt.peachcloud.org/peach_pub.gpg | sudo apt-key add -
```

You can then install peach packages with apt-get:

```
apt-get update
apt-get install peach-oled
```
