# peach-vps config

Scripts for configuring the peachcloud vps for various hosting and automation.

Currently:
- debian repository of microservices


# setup debian repo
an idempotent script for initializing the debian repo on the vps
```
apt update
apt install git python python3-pip rsync
git clone https://github.com/peachcloud/peach-vps.git
cd peach-vps
pip3 install -r requirements.txt
python3 scripts/setup_debian_repo.py -i
```


# update debian repo
without the -i flag, the setup_debian_repo rebuilds all
microservices (cross-compiled to arm64) and re-adds them to the debian repo
```
cd peach-vps
python3 scripts/setup_debian_repo.py
```


# using the debian repo on the pi
To add the peachcloud debian repo as an apt source,
on the pi,
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