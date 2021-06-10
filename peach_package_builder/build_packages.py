import argparse

from peach_package_builder.build_rust_packages import build_rust_packages
from peach_package_builder.build_peach_config import build_peach_config


def build_packages(default_branch=False, package=None):
    """
    builds all PeachCloud microservices as .deb files and adds them to the freight repo
    :param default_branch: checks out main git branch if True
    :param package: if provided, only builds this package
    """
    build_rust_packages(default_branch=default_branch, package=package)
    # only build peach-config if no package argument was provided or if peach-config is what is being built
    if not package or package == 'peach-config':
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
    parser.add_argument(
        "-p",
        "--package",
        help="Ensure default branch for all repos for build",
    )
    args = parser.parse_args()
    build_packages(default_branch=args.default, package=args.package)