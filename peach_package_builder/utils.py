import os
import jinja2
import subprocess

from peach_package_builder.constants import *


template_path = os.path.join(PROJECT_PATH, 'conf/templates')
template_loader = jinja2.FileSystemLoader(searchpath=template_path)
template_env = jinja2.Environment(loader=template_loader, keep_trailing_newline=True)


def render_template(src, dest, template_vars=None):
    """
    :param src: relative string path to jinja template file
    :param dest: absolute string path of output destination file
    :param template_vars: variables to render template with
    :return: None
    """
    template = template_env.get_template(src)
    if not template_vars:
        template_vars= {}
    output_text = template.render(**template_vars)
    if os.path.exists(dest):
        os.remove(dest)
    with open(dest, 'w') as f:
        f.write(output_text)


def add_deb_to_freight(package_name, package_path):
    print("[ ADDING PACKAGE {} ]".format(package_name))
    subprocess.check_call(["freight", "add", "-c", FREIGHT_CONF, package_path, "apt/buster"])


def update_freight_cache():
    print("[ ADDING PACKAGES TO FREIGHT CACHE ]")
    # needs to be run as sudo user
    subprocess.call(["sudo", "freight", "cache", "-g",
                     GPG_KEY_EMAIL, "-p", GPG_KEY_PASS_FILE])