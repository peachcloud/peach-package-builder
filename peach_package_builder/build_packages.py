import argparse

from peach_package_builder.build_rust_packages import build_rust_packages
from peach_package_builder.build_peach_config import build_peach_config


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