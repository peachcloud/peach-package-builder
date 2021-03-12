"""
script to build the peach-config debian module and add it to the freight repository
"""
import argparse
import subprocess
import sys
import os

from peach_package_builder.constants import *
from peach_package_builder.utils import add_deb_to_freight, update_freight_cache


def build_peach_config(default_branch=True):
    service_path = os.path.join(MICROSERVICES_SRC_DIR, "peach-config")
    if default_branch:
        # because some repo have main as default and some as master, we get the default
        default_branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'origin/HEAD'],
                                                 cwd=service_path).decode(sys.stdout.encoding)
        branch = default_branch.replace('origin/', '').strip()
        subprocess.check_call(["git", "checkout", branch], cwd=service_path)
        subprocess.check_call(["git", "reset", "HEAD", "--hard"], cwd=service_path)
        subprocess.check_call(["git", "pull"], cwd=service_path)
    # remove old build dir
    subprocess.check_call([
            "rm",
            "-rf",
            os.path.join(service_path, 'deb_dist')
    ])
    # build .deb
    subprocess.check_call([
            "python3",
            "setup.py",
            "--command-packages=stdeb.command",
            "bdist_deb"
        ],
        cwd=service_path)
    version = "0.2.7"   # TODO: get this version number from the repo
    deb_name = "python3-peach-config_{version}-1_all.deb".format(version=version)
    debian_package_path = os.path.join(
        service_path,
        "deb_dist/{}".format(deb_name)
    )
    subprocess.check_call(["cp", debian_package_path, MICROSERVICES_DEB_DIR])
    add_deb_to_freight(package_name=debian_package_path, package_path=debian_package_path)
    update_freight_cache()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--default",
        help="Ensure default branch for all repos for build",
        action="store_true"
    )
    args = parser.parse_args()
    build_peach_config(default_branch=args.default)