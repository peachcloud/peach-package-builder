#!/usr/bin/env python3
from constants import *

import subprocess
import argparse
import sys
import os


parser = argparse.ArgumentParser()
parser.add_argument(
    "-d",
    "--default",
    help="Ensure default branch for all repos for build",
    action="store_true"
)
args = parser.parse_args()


print("[ BUILDING AND UPDATING MICROSERVICE PACKAGES ]")
for service in SERVICES:
    service_name = service["name"]
    service_path = os.path.join(MICROSERVICES_SRC_DIR, service_name)
    print("[ BUILIDING SERVICE {} ]".format(service_name))
    # this arg ensures we build the default branch, otherwise we build what ever is found locally
    if args.default:
        # because some repo have main as default and some as master, we get the default
        default_branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'origin/HEAD'],
                                                 cwd=service_path).decode(sys.stdout.encoding)
        print("default: {}".format(default_branch))
        branch = default_branch.replace('origin/', '').strip()
        print("branch: {}".format(branch))
        subprocess.run(["git", "checkout", branch], cwd=service_path)
        subprocess.run(["git", "reset", "HEAD", "--hard"], cwd=service_path)
        subprocess.run(["git", "pull"], cwd=service_path)
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
