# peach-vps config

Code for configuring the peachcloud vps for various hosting and automation
- debian repository of microservices
- mdbook builder for devdocs


# setup
```
apt update
apt install git python python3-pip rsync
git clone https://github.com/peachcloud/peach-vps.git
cd peach-vps
pip3 install -r requirements.txt
python peach_vps_scripts/setup_vps.py
```


# update
(for more frequent updates that don't involve the whole initial setup)
```
cd peach-vps
python peach_vps_scripts/update_vps.py
```