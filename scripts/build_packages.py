#!/usr/bin/env python3
from constants import *

import subprocess
import os


print("[ BUILDING AND UPDATING MICROSERVICE PACKAGES ]")
for service in SERVICES:
    service_name = service["name"]
    service_path = os.path.join(MICROSERVICES_SRC_DIR, service_name)
    print("[ BUILIDING SERVICE {} ]".format(service_name))
    subprocess.call(["git", "pull"], cwd=service_path)
    debian_package_path = subprocess.run(
        [
            CARGO_PATH,
            "deb",
            "--target",
            "aarch64-unknown-linux-gnu"],
        cwd=service_path,
        stdout=subprocess.PIPE).stdout.decode("utf-8").strip()
    subprocess.call(["cp", debian_package_path, MICROSERVICES_DEB_DIR])

print("[ ADDING PACKAGES TO FREIGHT LIBRARY ]")
for package in os.scandir(MICROSERVICES_DEB_DIR):
    if package.name.endswith(".deb"):
        print("[ ADDING PACKAGE {} ]".format(package.name))
        subprocess.call(["freight", "add", "-c", FREIGHT_CONF,
                         package.path, "apt/buster"])

print("[ ADDING PACKAGES TO FREIGHT CACHE ]")
# needs to be run as sudo user
subprocess.call(["sudo", "freight", "cache", "-g",
                 GPG_KEY_EMAIL, "-p", GPG_KEY_PASS_FILE])

print("[ MICROSERVICE PACKAGE ARCHIVE UPDATED ]")
