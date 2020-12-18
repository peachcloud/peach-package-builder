#!/usr/bin/env python3

import subprocess
import os


GPG_KEY_EMAIL = "andrew@mycelial.technology"
# save the key passphrase to file and assign the path here:
# (ensure the file is only readable by the user running freight)
GPG_KEY_PASS_FILE = "/home/rust/passphrase.txt"


FREIGHT_CONF = "/etc/freight.conf"
MICROSERVICES_SRC_DIR = "/srv/peachcloud/automation/microservices"
MICROSERVICES_DEB_DIR = "/srv/peachcloud/debs"
USER_PATH = "/home/rust"


SERVICES = [
    {"name": "peach-buttons",
     "repo_url": "https://github.com/peachcloud/peach-buttons.git"},
    {"name": "peach-menu", "repo_url": "https://github.com/peachcloud/peach-menu.git"},
    {"name": "peach-monitor",
     "repo_url": "https://github.com/peachcloud/peach-monitor.git"},
    {"name": "peach-network",
     "repo_url": "https://github.com/peachcloud/peach-network.git"},
    {"name": "peach-oled", "repo_url": "https://github.com/peachcloud/peach-oled.git"},
    {"name": "peach-stats", "repo_url": "https://github.com/peachcloud/peach-stats.git"},
    # {"name": "peach-web", "repo_url": "https://github.com/peachcloud/peach-web.git"}, # currently build fails because it needs rust nightly for pear
]

cargo_path = os.path.join(USER_PATH, ".cargo/bin/cargo")

print("\n[ BUILDING AND UPDATING MICROSERVICE PACKAGES ]\n")
for service in SERVICES:
    service_name = service["name"]
    service_path = os.path.join(MICROSERVICES_SRC_DIR, service_name)
    print("\n[ BUILIDING SERVICE {} ]\n".format(service_name))
    subprocess.call(["git", "pull"], cwd=service_path)
    debian_package_path = subprocess.run(
        [
            cargo_path,
            "deb",
            "--target",
            "aarch64-unknown-linux-gnu"],
        cwd=service_path,
        stdout=subprocess.PIPE).stdout.decode("utf-8").strip()
    subprocess.call(["cp", debian_package_path, MICROSERVICES_DEB_DIR])

print("\n[ ADDING PACKAGES TO FREIGHT LIBRARY ]\n")
for package in os.scandir(MICROSERVICES_DEB_DIR):
    if package.name.endswith(".deb"):
        print("\n[ ADDING PACKAGE {} ]\n".format(package.name))
        subprocess.call(["freight", "add", "-c", FREIGHT_CONF,
                         package.path, "apt/buster"])

print("\n[ ADDING PACKAGES TO FREIGHT CACHE ]\n")
# needs to be run as sudo user
subprocess.call(["sudo", "freight", "cache", "-g",
                 GPG_KEY_EMAIL, "-p", GPG_KEY_PASS_FILE])

print("\n[ MICROSERVICE PACKAGE ARCHIVE UPDATED ]")
