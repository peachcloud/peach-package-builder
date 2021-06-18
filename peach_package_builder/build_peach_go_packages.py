"""
script to create debian packages for cross-compiled go binaries for go-sbot
based off of this post
https://unix.stackexchange.com/questions/627689/how-to-create-a-debian-package-from-a-bash-script-and-a-systemd-service
"""
import subprocess
import argparse
import re
import shutil
import sys
from packaging import version as pversion

from peach_package_builder.constants import *
from peach_package_builder.utils import render_template, add_deb_to_freight, update_freight_cache

# manually update this version when we want to build a new peach-go-sbot package
PEACH_GO_SBOT_VERSION = '0.1.5'
PEACH_GO_SSB_ROOM_VERSION = '0.1.7'


def crosscompile_peach_go_sbot(src_dir):
    subprocess.check_call(["git", "pull"], cwd=src_dir)
    print("[CROSS-COMPILING sbotcli]")
    subprocess.check_call(["env", "GOOS=linux", "GOARCH=arm64", "go", "build", "./cmd/sbotcli"], cwd=src_dir)
    print("[CROSS-COMPILING go-sbot]")
    subprocess.check_call(["env", "GOOS=linux", "GOARCH=arm64", "go", "build", "./cmd/go-sbot"], cwd=src_dir)


def crosscompile_peach_go_ssb_room(src_dir):
    subprocess.check_call(["git", "pull"], cwd=src_dir)
    print("[CROSS-COMPILING go-ssb-room/server]")
    subprocess.check_call(["env", "CGO_ENABLED=1", "CC=aarch64-linux-gnu-gcc",
                           "CC_FOR_TARGET=gcc-aarch64-linux-gnu", "GOOS=linux",
                           "GOARCH=arm64", "go", "build", "./cmd/server"], cwd=src_dir)


def package_go_package(src_dir, package_name, deb_conf_dir, build_dir, go_binary_names, version):
    print("[ PACKAGING {} ]".format(package_name))
    # copy debian conf files into correct locations in package build directory
    DEBIAN_SRC_DIR = os.path.join(deb_conf_dir, 'DEBIAN')
    DEBIAN_DEST_DIR = os.path.join(build_dir, 'DEBIAN')
    os.makedirs(DEBIAN_DEST_DIR)
    maintainer_scripts = ['postinst', 'postrm', 'prerm']
    for script in maintainer_scripts:
        src = os.path.join(DEBIAN_SRC_DIR, script)
        dest = os.path.join(DEBIAN_DEST_DIR, script)
        shutil.copyfile(src, dest)
        subprocess.check_call(["chmod", "775", dest])
    # copy control file putting in correct version number
    src = os.path.join(package_name.replace("-", "_"), "DEBIAN/control")
    dest = os.path.join(DEBIAN_DEST_DIR, "control")
    render_template(src=src, dest=dest, template_vars={"version": version})

    # copy systemd service file
    SERVICE_DIR = os.path.join(build_dir, 'lib/systemd/system')
    os.makedirs(SERVICE_DIR)
    shutil.copyfile(
        os.path.join(deb_conf_dir, '{}.service'.format(package_name)),
        os.path.join(SERVICE_DIR, '{}.service'.format(package_name))
    )

    # copy cross-compiled binaries
    BIN_DIR = os.path.join(build_dir, 'usr/bin')
    os.makedirs(BIN_DIR)
    for go_binary_src, go_binary_dest in go_binary_names:
        destination = os.path.join(BIN_DIR, go_binary_dest)
        shutil.copyfile(
            os.path.join(os.path.join(src_dir), go_binary_src),
            destination
        )
        subprocess.check_call(["chmod", "770", destination])

    # create deb package
    deb_file_name = "{}_{}_arm64.deb".format(package_name, version)
    print("[ CREATING {}]".format(deb_file_name))
    subprocess.check_call(["dpkg-deb", "-b", ".", deb_file_name], cwd=build_dir)

    # copy deb package to MICROSERVICES_DEB_DIR
    deb_path = os.path.join(build_dir, deb_file_name)
    subprocess.check_call(["cp", deb_path, MICROSERVICES_DEB_DIR])

    # add deb package to freight
    add_deb_to_freight(package_name=deb_file_name, package_path=deb_path)

    # update freight cache
    update_freight_cache()


def build_peach_go_sbot():

    # constants
    DEB_CONF_DIR = os.path.join(PROJECT_PATH, 'conf/templates/peach_go_sbot')
    DEB_BUILD_DIR = "/tmp/peach_go_sbot"
    # GO_BINARIES is a list of tuples of src_name and dest_name,
    # which will be callable via /usr/bin/dest_name after installation
    GO_BINARIES = [('go-sbot', 'go-sbot'), ('sbotcli', 'sbotcli')]
    SRC_DIR = "/srv/peachcloud/automation/go-ssb"

    # gets the most recently built peach_go_sbot version, and increments the micro-number by 1
    version = PEACH_GO_SBOT_VERSION
    print("[ BUILDING PEACH-GO-SBOT VERSION {}]".format(version))

    # delete build directory if it already exists or create it
    subprocess.check_call(["rm", "-rf", DEB_BUILD_DIR])
    if not os.path.exists(DEB_BUILD_DIR):
        os.makedirs(DEB_BUILD_DIR)

    # cross-compile and package peach-go-sbot with new version number
    crosscompile_peach_go_sbot(src_dir=SRC_DIR)
    package_go_package(src_dir=SRC_DIR,
                       package_name="peach-go-sbot",
                       deb_conf_dir=DEB_CONF_DIR,
                       build_dir=DEB_BUILD_DIR,
                       go_binary_names=GO_BINARIES,
                       version=version)


def build_peach_go_ssb_room():

    # constants
    DEB_CONF_DIR = os.path.join(PROJECT_PATH, 'conf/templates/peach_go_ssb_room')
    DEB_BUILD_DIR = "/tmp/peach_go_ssb_room"
    # GO_BINARIES is a list of tuples of src_name and dest_name,
    # which will be callable via /usr/bin/dest_name after installation
    GO_BINARIES = [('server', 'go-ssb-room-server')]
    SRC_DIR = "/srv/peachcloud/automation/go-ssb-room"

    # gets the most recently built peach_go_sbot version, and increments the micro-number by 1
    version = PEACH_GO_SSB_ROOM_VERSION
    print("[ BUILDING PEACH-GO-SSB-ROOM VERSION {}]".format(version))

    # delete build directory if it already exists or create it
    subprocess.check_call(["rm", "-rf", DEB_BUILD_DIR])
    if not os.path.exists(DEB_BUILD_DIR):
        os.makedirs(DEB_BUILD_DIR)

    # cross-compile and package peach-go-sbot with new version number
    crosscompile_peach_go_ssb_room(src_dir=SRC_DIR)
    package_go_package(src_dir=SRC_DIR,
                       package_name="peach-go-ssb-room",
                       deb_conf_dir=DEB_CONF_DIR,
                       build_dir=DEB_BUILD_DIR,
                       go_binary_names=GO_BINARIES,
                       version=version)


if __name__ == '__main__':
    # build_peach_go_sbot()
    build_peach_go_ssb_room()

