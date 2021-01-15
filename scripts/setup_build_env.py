#!/usr/bin/env python3

from utils import render_template
from constants import *

import subprocess
import argparse
import os


# parse CLI args
parser = argparse.ArgumentParser()
parser.add_argument(
    "-u",
    "--update",
    help="Update Rust installation",
    action="store_true"
)
args = parser.parse_args()


# update rust installation
if args.update:
    print("[ UPDATING RUST ]")
    rustup_path = os.path.join(USER_PATH, ".cargo/bin/rustup")
    if not os.path.exists(rustup_path):
        print("rustup installation not found")
        print("rerun this script without the '-u' flag to install rust")
    else:
        subprocess.call([rustup_path, "update"])
else:
    # initialize debian package build environment from a blank slate
    # (but this code is idempotent so it can be re-run if already initialized)
    print("[ INSTALLING SYSTEM REQUIREMENTS ]")
    subprocess.call(["sudo",
                     "apt-get",
                     "install",
                     "git",
                     "nginx",
                     "curl",
                     "build-essential",
                     "gcc-aarch64-linux-gnu",
                     ])

    print("[ CREATING DIRECTORIES ]")
    folders = [MICROSERVICES_SRC_DIR, FREIGHT_CACHE, FREIGHT_LIB]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)

    print("[ INSTALLING RUST ]")
    rustc_path = os.path.join(USER_PATH, ".cargo/bin/rustc")
    if not os.path.exists(rustc_path):
        first_command = subprocess.Popen(
            ["curl", "https://sh.rustup.rs", "-sSf"], stdout=subprocess.PIPE)
        output = subprocess.check_output(
            ["sh", "-s", "--", "-y"], stdin=first_command.stdout)
        first_command.wait()

    print("[ INSTALLING CARGO-DEB ]")
    cargo_deb_path = os.path.join(USER_PATH, ".cargo/bin/cargo-deb")
    if not os.path.exists(cargo_deb_path):
        subprocess.call([CARGO_PATH, "install", "cargo-deb"])

    print("[ INSTALL TOOLCHAIN FOR CROSS-COMPILATION ]")
    rustup_path = os.path.join(USER_PATH, ".cargo/bin/rustup")
    subprocess.call([rustup_path, "target", "add",
                     "aarch64-unknown-linux-gnu"])
    subprocess.call([rustup_path, "toolchain", "install",
                     "nightly-aarch64-unknown-linux-gnu"])

    print("[ INSTALLING FREIGHT ]")
    freight_path = os.path.join(AUTOMATION_DIR, "freight")
    if not os.path.exists(freight_path):
        subprocess.call(
            ["git", "clone", "https://github.com/freight-team/freight.git", freight_path])

    print("[ CONFIGURING FREIGHT ]")
    freight_conf_tmp_path = os.path.join(USER_PATH, "freight.conf")
    render_template(
        src="freight.conf",
        dest=freight_conf_tmp_path,
        template_vars={
            "freight_lib_path": FREIGHT_LIB,
            "freight_cache_path": FREIGHT_CACHE,
            "gpg_key_email": GPG_KEY_EMAIL
        }
    )
    subprocess.call(["sudo", "cp", freight_conf_tmp_path, FREIGHT_CONF])

    print("[ PULLING MICROSERVICES CODE FROM GITHUB ]")
    for service in SERVICES:
        name = service["name"]
        repo_url = service["repo_url"]
        service_path = os.path.join(MICROSERVICES_SRC_DIR, name)
        if not os.path.exists(service_path):
            subprocess.call(["git", "clone", repo_url, service_path])

    print("[ EXPORTING PUBLIC GPG KEY ]")
    output_path = "{}/pubkey.gpg".format(FREIGHT_CACHE)
    if not os.path.exists(output_path):
        subprocess.call(["gpg", "--armor", "--output",
                         output_path, "--export", GPG_KEY_EMAIL])

    print("[ COPYING NGINX CONFIG ]")
    nginx_conf_tmp_path = os.path.join(USER_PATH, "apt.peachcloud.org")
    render_template(
        src="nginx_debian.conf",
        dest=nginx_conf_tmp_path,
        template_vars={
            "apt_dir": FREIGHT_CACHE
        }
    )
    subprocess.call(["sudo", "cp", nginx_conf_tmp_path,
                     "/etc/nginx/sites-enabled/apt.peachcloud.org"])

    print("[ DEBIAN PACKAGE BUILD ENVIRONMENT SETUP COMPLETE ]")
