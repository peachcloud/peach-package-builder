# peach-vps

![Generic badge](https://img.shields.io/badge/version-0.2.1-<COLOR>.svg)

Scripts for configuring the PeachCloud VPS for various hosting and automation functions.

Currently:

 - Debian repository of microservices

## Setup Debian Repo

`scripts/setup_debian_repo.py`

An idempotent script for initializing the Debian repo on the VPS.

The script currently performs the following actions:

 - Installs system requirements
 - Creates directories for microservices and package archive
 - Installs Rust
 - Installs `cargo deb`
 - Installs Rust aarch64 toolchain for cross-compilation
 - Installs Freight for package archive creation and management
 - Configures Freight
 - Pulls microservices code from GitHub repos
 - Exports the public GPG key
 - Configures nginx
 - Builds and updates microservice packages
 - Adds packages to Freight library
 - Adds packages to Freight cache

Prior to executing the script for the first time, run the following commands on the target system:

```
sudo apt update
sudo apt install git python python3-pip rsync
git clone https://github.com/peachcloud/peach-vps.git
cd peach-vps
pip3 install -r requirements.txt
```

Open `scripts/setup_debian_repo.py` and set the following constants:

 - USER_PATH
 - GPG_KEY_EMAIL
 - GPG_KEY_PASS_FILE

Then execute the script with the `-i` flag to run the full system initialization process (_note: several commands executed by the script require `sudo` permissions. You will be prompted for the user password during the execution of the scipt._):

```
python3 -u scripts/setup_debian_repo.py -i
```

## Update Debian Repo

Without the -i flag, the `setup_debian_repo.py` script rebuilds all
microservices (cross-compiled to arm64) and updates the Debian repo

```
cd peach-vps
python3 -u scripts/setup_debian_repo.py
```

## Install from Debian Repo

To add the PeachCloud Debian repo as an apt source, run the following commands from your Pi:

```
vi /etc/apt/sources.list.d/peach.list
```

Append the following line:

```
deb http://apt.peachcloud.org/debian/ buster main
```

Add the gpg pub key to the apt-key list:

```
wget -O - http://apt.peachcloud.org/peach_pub.gpg | sudo apt-key add -
```

You can then install peach packages with apt:

```
sudo apt update
sudo apt install peach-oled
```

By default, the latest version of the package will be downloaded and installed.

Specific versions of packages can be selected for installation by supplying the semantic versioning number (this is useful for downgrading):

```
sudo apt install peach-network=0.2.0
```

## Licensing

AGPL-3.0
