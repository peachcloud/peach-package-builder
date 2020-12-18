# peach-vps

![Generic badge](https://img.shields.io/badge/version-0.3.0-<COLOR>.svg)

Scripts for configuring the PeachCloud VPS for various hosting and automation functions.

## Setup Build Environment

`scripts/setup_build_env.py`

An idempotent script for initializing a build and deployment environment for PeachCloud packages.

The script currently performs the following actions:

 - Installs system requirements
 - Creates directories for microservices and package archive
 - Installs Rust
 - Installs `cargo deb`
 - Installs Rust aarch64 toolchain for cross-compilation
 - Installs [Freight](https://github.com/freight-team/freight) for package archive creation and management
 - Configures Freight
 - Pulls microservices code from GitHub repos
 - Exports the public GPG key
 - Configures nginx

The script can also be run with the optional `-u` flag (`--update`) to update the Rust compiler and installed toolchains.

**NB:** Prior to executing the script for the first time, run the following commands on the target system:

```
sudo apt update
sudo apt install git python python3-pip rsync
git clone https://github.com/peachcloud/peach-vps.git
cd peach-vps
pip3 install -r requirements.txt
```

Open `scripts/setup_build_env.py` and set the following constants:

 - USER_PATH
 - GPG_KEY_EMAIL
 - GPG_KEY_PASS_FILE

Then execute the script to run the full system initialization process (_note: several commands executed by the script require `sudo` permissions. You will be prompted for the user password during the execution of the scipt._):

```
python3 -u scripts/setup_build_env.py
```

## Build and Serve Debian Packages

`scripts/build_packages.py`

An idempotent script for building the latest versions of all PeachCloud packages and adding them to the Debian package archive.

The script currently performs the following actions:

 - Builds and updates microservice packages
 - Adds packages to Freight library
 - Adds packages to Freight cache

```
python3 -u scripts/build_packages.py
```

Freight supports the ability to have multiple versions of a package in a single Debian package archive. If a particular version of a package already exists in the Freight library, it will not be readded or overwritten.

## Install Packages from Debian Package Archive

To add the PeachCloud Debian package archive as an apt source, run the following commands from your Pi:

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
