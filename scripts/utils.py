import os
import jinja2
import subprocess

PROJECT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
print('PROJECT_PATH: {}'.format(PROJECT_PATH))

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


