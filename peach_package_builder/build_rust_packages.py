#!/usr/bin/env python3
import subprocess
import argparse
import sys
import os

from peach_package_builder.build_peach_config import build_peach_config
from peach_package_builder.constants import *
from peach_package_builder.utils import add_deb_to_freight, update_freight_cache


def add_debs_dir_to_freight():
    """
    adds all packages in MICROSERVICES_DEB_DIR to freight cache
    """
    print("[ ADDING PACKAGES TO FREIGHT LIBRARY ]")
    for package in os.scandir(MICROSERVICES_DEB_DIR):
        if package.name.endswith(".deb"):
            add_deb_to_freight(package_name=package.name, package_path=package.path)
    update_freight_cache()


def build_rust_packages(default_branch=False, package=None):
    """
    builds all PeachCloud microservices written in rust and copies them to MICROSERVICES_DEB_DIR
    :param default_branch: checks out main git branch if True
    :param package: if provided, only builds this package
    """
    print("[ BUILDING AND UPDATING RUST MICROSERVICE PACKAGES ]")
    # if package argument was provided, then only build that one package, otherwise build all packages
    if package:
        services = filter(lambda s: s["name"] == package, SERVICES)
    else:
        services = SERVICES
    for service in services:
        service_name = service["name"]
        service_path = os.path.join(MICROSERVICES_SRC_DIR, service_name)
        print("[ BUILIDING SERVICE {} ]".format(service_name))
        # this arg ensures we build the default branch, otherwise we build what ever is found locally
        if default_branch:
            remote_branch = 'origin/main'
            branch = 'main'
            subprocess.check_call(["git", "reset", "HEAD", "--hard"])
            subprocess.check_call(["git", "checkout", branch], cwd=service_path)
            subprocess.check_call(["git", "fetch", "--all"], cwd=service_path)
            subprocess.check_call(["git", "reset", "--hard", remote_branch], cwd=service_path)
        debian_package_path = subprocess.check_output(
            [
                CARGO_PATH,
                "deb",
                "--target",
                "aarch64-unknown-linux-gnu"],
            cwd=service_path).decode("utf-8").strip()
        subprocess.call(["cp", debian_package_path, MICROSERVICES_DEB_DIR])

        # add deb to freight
        package_name = os.path.basename(debian_package_path)
        add_deb_to_freight(package_name=package_name, package_path=debian_package_path)

    # update freight cache
    update_freight_cache()


def build_packages(default_branch=False):
    """
    builds all PeachCloud microservices as .deb files and adds them to the freight repo
    """
    build_rust_packages(default_branch=default_branch)
    build_peach_config(default_branch=default_branch)
    print("[ MICROSERVICE PACKAGE ARCHIVE UPDATED ]")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--default",
        help="Ensure default branch for all repos for build",
        action="store_true"
    )
    args = parser.parse_args()
    build_packages(default_branch=args.default)