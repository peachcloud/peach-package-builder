#!/usr/bin/env python3
"""
script to create debian packages for cross-compiled go binaries for go-sbot
based off of this post
https://unix.stackexchange.com/questions/627689/how-to-create-a-debian-package-from-a-bash-script-and-a-systemd-service
"""
import subprocess
import argparse
import sys
import os
import shutil

from peach_package_builder.constants import *
from peach_package_builder.utils import render_template, add_deb_to_freight, update_freight_cache


DEB_CONF_DIR = os.path.join(PROJECT_PATH, 'conf/templates/peach_go_sbot')
DEB_BUILD_DIR = "/tmp/peach_go_sbot"
GO_SSB_DIR = "/srv/peachcloud/automation/go-ssb"


def crosscompile_peach_go_sbot():
    subprocess.check_call(["git", "pull"], cwd=GO_SSB_DIR)
    # TODO: confirm that version number in the repo matches the version number we set for the package we are building
    print("[CROSS-COMPILING sbotcli]")
    subprocess.check_call(["env", "GOOS=linux", "GOARCH=arm64", "go", "build", "./cmd/sbotcli"], cwd=GO_SSB_DIR)
    print("[CROSS-COMPILING go-sbot]")
    subprocess.check_call(["env", "GOOS=linux", "GOARCH=arm64", "go", "build", "./cmd/go-sbot"], cwd=GO_SSB_DIR)


def package_peach_go_sbot(version):

    print("[ PACKAGING peach-go-sbot ]")
    # copy debian conf files into correct locations in package build directory
    DEBIAN_SRC_DIR = os.path.join(DEB_CONF_DIR, 'DEBIAN')
    DEBIAN_DEST_DIR = os.path.join(DEB_BUILD_DIR, 'DEBIAN')
    os.makedirs(DEBIAN_DEST_DIR)
    maintainer_scripts = ['postinst', 'postrm', 'prerm']
    for script in maintainer_scripts:
        src = os.path.join(DEBIAN_SRC_DIR, script)
        dest = os.path.join(DEBIAN_DEST_DIR, script)
        shutil.copyfile(src, dest)
        subprocess.check_call(["chmod", "775", dest])
    # copy control file putting in correct version number
    src = os.path.join("peach_go_sbot/DEBIAN/control")
    dest = os.path.join(DEBIAN_DEST_DIR, "control")
    render_template(src=src, dest=dest, template_vars={"version": version})

    # copy systemd service file
    SERVICE_DIR = os.path.join(DEB_BUILD_DIR, 'lib/systemd/system')
    os.makedirs(SERVICE_DIR)
    shutil.copyfile(
        os.path.join(DEB_CONF_DIR, 'peach-go-sbot.service'),
        os.path.join(SERVICE_DIR, 'peach-go-sbot.service')
    )

    # copy cross-compiled binaries
    GO_BINARIES = ['go-sbot', 'sbotcli']
    BIN_DIR = os.path.join(DEB_BUILD_DIR, 'usr/bin')
    os.makedirs(BIN_DIR)
    for go_binary in GO_BINARIES:
        destination = os.path.join(BIN_DIR, go_binary)
        shutil.copyfile(
            os.path.join(os.path.join(GO_SSB_DIR), go_binary),
            destination
        )
        subprocess.check_call(["chmod", "770", destination])

    # create deb package
    deb_file_name = "peach-go-sbot_{}_arm64.deb".format(version)
    print("[ CREATING {}]".format(deb_file_name))
    subprocess.check_call(["dpkg-deb", "-b", ".", deb_file_name], cwd=DEB_BUILD_DIR)

    # copy deb package to MICROSERVICES_DEB_DIR
    deb_path = os.path.join(DEB_BUILD_DIR, deb_file_name)
    subprocess.check_call(["cp", deb_path, MICROSERVICES_DEB_DIR])

    # add deb package to freight
    add_deb_to_freight(package_name=deb_file_name, package_path=deb_path)

    # update freight cache
    update_freight_cache()


def build_peach_go_sbot():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--version",
        help="Set version number for go-sbot",
    )
    args = parser.parse_args()

    print("[ BUILDING PEACH-GO-SBOT VERSION {}]".format(args.version))

    # delete build directory if it already exists or create it
    subprocess.check_call(["rm", "-rf", DEB_BUILD_DIR])
    if not os.path.exists(DEB_BUILD_DIR):
        os.makedirs(DEB_BUILD_DIR)

    crosscompile_peach_go_sbot()
    package_peach_go_sbot(version=args.version)



if __name__ == '__main__':
    build_peach_go_sbot()

