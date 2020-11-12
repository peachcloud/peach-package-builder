from utils import render_template

import subprocess
import os

INITIALIZE_DEBIAN_REPO = True

MICROSERVICES_SRC_DIR = "/srv/peachcloud/automation/microservices"
WEB_DIR = "/var/www/"
APT_DIR = "/var/www/repos/apt"
DEBIAN_REPO_DIR = "/var/www/repos/apt/debian"
DEBIAN_REPO_CONF_DIR = "/var/www/repos/apt/debian/conf"

# before running this script run `gpg --gen-key` on the server, and put the key id here
# `gpg --list-keys`
GPG_KEY_ID = "4ACEF251EA3E091167E8F03EBF69A52BE3565476"

SERVICES = [
    {"name": "peach-oled", "repo_url": "https://github.com/peachcloud/peach-oled.git"},
    {"name": "peach-network", "repo_url": "https://github.com/peachcloud/peach-network.git"}
]

if INITIALIZE_DEBIAN_REPO:

    print("[ INSTALLING SYSTEM REQUIREMENTS ]")
    subprocess.call(["apt-get", "install", "git", "nginx", "curl", "build-essential", "reprepro", "gcc-aarch64-linux-gnu", ])

    print("[ CREATING DIRECTORIES ]")
    folders = [MICROSERVICES_SRC_DIR, WEB_DIR, APT_DIR, DEBIAN_REPO_DIR, DEBIAN_REPO_CONF_DIR]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)

    print("[ INSTALLING RUST ]")
    if not os.path.exists("/root/.cargo/bin/rustc"):
        first_command = subprocess.Popen(["curl", "https://sh.rustup.rs", "-sSf"], stdout=subprocess.PIPE)
        output = subprocess.check_output(["sh", "-s", "--", "-y"], stdin=first_command.stdout)
        first_command.wait()

    print("[ INSTALLING CARGO-DEB ]")
    if not os.path.exists("/root/.cargo/bin/cargo-deb"):
        subprocess.call(["/root/.cargo/bin/cargo", "install", "cargo-deb"])

    print("[ INSTALL TOOLCHAIN FOR CROSS-COMPILATION ]")
    subprocess.call(["/root/.cargo/bin/rustup", "target", "add", "aarch64-unknown-linux-gnu"])
    subprocess.call(["/root/.cargo/bin/rustup", "toolchain", "install", "nightly-aarch64-unknown-linux-gnu"])

    print("[ PULLING MICROSERVICES CODE FROM GITHUB ]")
    for service in SERVICES:
        name = service["name"]
        repo_url = service["repo_url"]
        service_path = os.path.join(MICROSERVICES_SRC_DIR, name)
        if not os.path.exists(service_path):
            subprocess.call(["git", "clone", repo_url, service_path])

    print("[ COPYING DEBIAN REPO CONFIG ]")
    render_template(
        src="debian_repo/distributions",
        dest="{}/distributions".format(DEBIAN_REPO_CONF_DIR),
        template_vars={
            "gpg_key_id": GPG_KEY_ID
        }
    )
    render_template(
        src="debian_repo/options",
        dest="{}/options".format(DEBIAN_REPO_CONF_DIR),
        template_vars={
            "debian_rep_dir": DEBIAN_REPO_DIR
        }
    )
    render_template(
        src="debian_repo/override.buster",
        dest="{}/override.buster".format(DEBIAN_REPO_CONF_DIR),
        template_vars={
            "services": [service["name"] for service in SERVICES]
        }
    )

    print("[ EXPORTING PUBLIC GPG KEY ]")
    output_path = "{}/peach_pub.gpg".format(APT_DIR)
    if not os.path.exists(output_path):
        subprocess.call(["gpg", "--armor", "--output", output_path, "--export", GPG_KEY_ID])

    print("[ COPYING NGINX CONFIG ]")
    render_template(
        src="debian_repo/nginx_debian.conf",
        dest="/etc/nginx/sites-enabled/deb.peachcloud.org",
        template_vars = {
            "apt_dir": APT_DIR
        }
    )


# below is code for updating the microservices, building the microservices,
# and adding them to the debian repo
for service in SERVICES:
    service_name = service["name"]
    service_path = os.path.join(MICROSERVICES_SRC_DIR, service_name)
    print("[ BUILIDING SERVICE {} ]".format(service_name))
    subprocess.call(["git", "pull"], cwd=service_path)
    debian_package_path = str(subprocess.check_output(["/root/.cargo/bin/cargo", "deb", "--target", "aarch64-unknown-linux-gnu"], cwd=service_path))
    print('OUTPUT: {}'.format(debian_package_path))
    subprocess.call("reprepro includedeb buster {deb_path}".format(
        debian_dir=DEBIAN_REPO_DIR,
        deb_path=debian_package_path
    ), cwd=DEBIAN_REPO_DIR)


