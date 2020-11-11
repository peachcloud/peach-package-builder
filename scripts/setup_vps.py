from utils import render_template, cargo_install
from vars import VARS

import subprocess
import os
import pwd
import grp


print("[ UPDATING OPERATING SYSTEM ]")
subprocess.check_call(["apt-get", "update", "-y"])
subprocess.check_call(["apt-get", "upgrade", "-y"])

print("[ INSTALLING SYSTEM REQUIREMENTS ]")
subprocess.check_call(["apt-get", "install", "git", "nginx", "curl", "build-essential", "mosh"])

print("[ CREATING SYSTEM GROUPS ]")
group = 'peach'
try:
    grp.getgrnam(group)
    # if group exists
except KeyError:
    # if group doesn't eixst
    subprocess.check_call(["/usr/sbin/groupadd", "peach"])

print("[ ADDING SYSTEM USER ]")
users = ["notplants", "glyph"]
for user in users:
    try:
        # if user exists
        pwd.getpwnam(user)
    except:
        # if user does not exist
        subprocess.check_call(["/usr/sbin/adduser", user])
        subprocess.check_call(["usermod", "-aG", "sudo", user])
        subprocess.check_call(["/usr/sbin/usermod", "-a", "-G", user, "peach"])

print("[ CREATING DIRECTORIES ]")
folders = [VARS["src_dir"], VARS["web_dir"], VARS["debian_rep_dir"]]
for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)

print("[ INSTALLING RUST ]")
if not os.path.exists('/root/.cargo/bin/rustc'):
    first_command = subprocess.Popen(["curl", "https://sh.rustup.rs", "-sSf"], stdout=subprocess.PIPE)
    output = subprocess.check_output(["sh", "-s", "--", "-y"], stdin=first_command.stdout)
    first_command.wait()

print("[ INSTALLING CARGO PACKAGES ]")
cargo_install("cargo-deb")

print("[ COPYING NGINX CONFIG ]")
render_template(src='nginx/nginx.conf', dest='/etc/nginx/nginx.conf')


