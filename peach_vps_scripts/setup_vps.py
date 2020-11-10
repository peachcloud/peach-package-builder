from peach_vps_scripts.utils import render_template, cargo_install
from peach_vps_scripts.vars import VARS

import subprocess
import os


print("[ UPDATING OPERATING SYSTEM ]")
subprocess.call(["apt-get", "update", "-y"])
subprocess.call(["apt-get", "upgrade", "-y"])

print("[ INSTALLING SYSTEM REQUIREMENTS ]")
subprocess.call(["apt-get", "install", "git", "nginx", "curl", "build-essential", "mosh"])

print("[ CREATING SYSTEM GROUPS ]")
subprocess.call(["/usr/sbin/groupadd", "peach"])

print("[ ADDING SYSTEM USER ]")
users = ["notplants", "glyph"]
for user in users:
    subprocess.call(["/usr/sbin/adduser", user])
    subprocess.call(["usermod", "-aG", "sudo", user])
    subprocess.call(["/usr/sbin/usermod", "-a", "-G", user, "peach"])

print("[ CREATING DIRECTORIES ]")
folders = [VARS["src_dir"], VARS["www_dir"], VARS["debian_repo_dir"]]
for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)

print("[ INSTALLING RUST ]")
subprocess.call(["curl", "https://sh.rustup.rs", "-sSf", "|", "sh", "-s", "--", "-y"])

print("[ INSTALLING CARGO PACKAGES ]")
cargo_install("cargo-deb")

render_template(src='nginx/nginx.conf', dest='/etc/nginx/nginx.conf')


