from utils import render_template

import subprocess
import os
import argparse


# constants
AUTOMATION_DIR = "/srv/peachcloud/automation"
MICROSERVICES_SRC_DIR = "/srv/peachcloud/automation/microservices"
MICROSERVICES_DEB_DIR = "/srv/peachcloud/debs"
FREIGHT_CONF = "/etc/freight.conf"
FREIGHT_LIB = "/var/lib/freight"
FREIGHT_CACHE = "/var/www/apt.peachcloud.org"
# define user path before running the script
USER_PATH = "/home/rust"

# before running this script run `gpg --gen-key` on the server
# assign the email address of the key id here:
GPG_KEY_EMAIL = "andrew@mycelial.technology"
# save the key passphrase to file and assign the path here:
# (ensure the file is only readable by the user running freight)
GPG_KEY_PASS_FILE = "/home/rust/passphrase.txt"
# if you need to list the existing keys: `gpg --list-keys`

SERVICES = [
    {"name": "peach-buttons", "repo_url": "https://github.com/peachcloud/peach-buttons.git"},
    {"name": "peach-menu", "repo_url": "https://github.com/peachcloud/peach-menu.git"},
    {"name": "peach-monitor", "repo_url": "https://github.com/peachcloud/peach-monitor.git"},
    {"name": "peach-network", "repo_url": "https://github.com/peachcloud/peach-network.git"},
    {"name": "peach-oled", "repo_url": "https://github.com/peachcloud/peach-oled.git"},
    {"name": "peach-stats", "repo_url": "https://github.com/peachcloud/peach-stats.git"},
    # {"name": "peach-web", "repo_url": "https://github.com/peachcloud/peach-web.git"}, # currently build fails because it needs rust nightly for pear
]

# parse CLI args
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--initialize", help="initialize and update debian repo", action="store_true")
args = parser.parse_args()

cargo_path = os.path.join(USER_PATH, ".cargo/bin/cargo")

# initializing debian repo from a blank slate
# (but this code is idempotent so it can be re-run if already initialized)
if args.initialize:

    print("[ INSTALLING SYSTEM REQUIREMENTS ]")
    subprocess.call(["sudo", "apt-get", "install", "git", "nginx", "curl", "build-essential", "gcc-aarch64-linux-gnu", ])

    print("[ CREATING DIRECTORIES ]")
    folders = [MICROSERVICES_SRC_DIR, FREIGHT_CACHE, FREIGHT_LIB]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)

    print("[ INSTALLING RUST ]")
    rustc_path = os.path.join(USER_PATH, ".cargo/bin/rustc")
    if not os.path.exists(rustc_path):
        first_command = subprocess.Popen(["curl", "https://sh.rustup.rs", "-sSf"], stdout=subprocess.PIPE)
        output = subprocess.check_output(["sh", "-s", "--", "-y"], stdin=first_command.stdout)
        first_command.wait()

    print("[ INSTALLING CARGO-DEB ]")
    cargo_deb_path = os.path.join(USER_PATH, ".cargo/bin/cargo-deb")
    if not os.path.exists(cargo_deb_path):
        subprocess.call([cargo_path, "install", "cargo-deb"])

    print("[ INSTALL TOOLCHAIN FOR CROSS-COMPILATION ]")
    rustup_path = os.path.join(USER_PATH, ".cargo/bin/rustup")
    subprocess.call([rustup_path, "target", "add", "aarch64-unknown-linux-gnu"])
    subprocess.call([rustup_path, "toolchain", "install", "nightly-aarch64-unknown-linux-gnu"])

    print("[ INSTALLING FREIGHT ]")
    freight_path = os.path.join(AUTOMATION_DIR, "freight")
    if not os.path.exists(freight_path):
        subprocess.call(["git", "clone", "https://github.com/freight-team/freight.git", freight_path])

    print("[ CONFIGURING FREIGHT ]")
    freight_conf_tmp_path = os.path.join(USER_PATH, "freight.conf")
    render_template(
        src="debian_repo/freight.conf",
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
    output_path = "{}/peach_pub.gpg".format(FREIGHT_CACHE)
    if not os.path.exists(output_path):
        subprocess.call(["gpg", "--armor", "--output", output_path, "--export", GPG_KEY_EMAIL])

    print("[ COPYING NGINX CONFIG ]")
    nginx_conf_tmp_path = os.path.join(USER_PATH, "apt.peachcloud.org")
    render_template(
        src="debian_repo/nginx_debian.conf",
        dest=nginx_conf_tmp_path,
        template_vars = {
            "apt_dir": FREIGHT_CACHE
        }
    )
    subprocess.call(["sudo", "cp", nginx_conf_tmp_path, "/etc/nginx/sites-enabled/apt.peachcloud.org"])

# update the microservices from git and build the debian packages
print("[ BUILDING AND UPDATING MICROSERVICE PACKAGES ]")
for service in SERVICES:
    service_name = service["name"]
    service_path = os.path.join(MICROSERVICES_SRC_DIR, service_name)
    print("[ BUILIDING SERVICE {} ]".format(service_name))
    subprocess.call(["git", "pull"], cwd=service_path)
    debian_package_path = subprocess.run([cargo_path, "deb", "--target", "aarch64-unknown-linux-gnu"], cwd=service_path, stdout=subprocess.PIPE).stdout.decode("utf-8").strip()
    # copy package to staging folder
    subprocess.call(["cp", debian_package_path, MICROSERVICES_DEB_DIR])

print("[ ADDING PACKAGES TO FREIGHT LIBRARY ]")
for package in MICROSERVICES_DEB_DIR:
    package_path = os.path.join(MICROSERVICES_DEB_DIR, package)
    print("[ ADDING PACKAGE {} ]".format(package))
    subprocess.call(["freight", "add", "-c", FREIGHT_CONF, package_path, "apt/buster"])

print("[ ADDING PACKAGES TO FREIGHT CACHE ]")
# needs to be run as sudo user
subprocess.call(["sudo", "freight", "cache", "-g", GPG_KEY_EMAIL, "-p", GPG_KEY_PASS_FILE])

print("[ DEBIAN REPO SETUP COMPLETE ]")
