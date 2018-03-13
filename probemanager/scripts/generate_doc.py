from django.apps.registry import apps
from jinja2 import Template
from home.models import Probe
import os
from django.conf import settings


def run(*args):
    template = """

{{ name }}
{% for char in range(name|length) -%}
~
{%- endfor %}

.. toctree::

   {{ module }}

"""
    template_include = """.. include:: ../../probemanager/{{ module }}/README.rst

"""
    t = Template(template)
    t_include = Template(template_include)
    with open(settings.ROOT_DIR + '/docs/modules/index.rst', 'w') as f:
        for app in apps.get_app_configs():
            for model in app.get_models():
                if issubclass(model, Probe):
                    if app.verbose_name != "Core":
                        path = settings.BASE_DIR + "/" + app.label + "/README.rst"
                        if os.path.isfile(path):
                            template_rendered = t.render(module=app.label, name=app.verbose_name)
                            template_include_rendered = t_include.render(module=app.label)
                            f_include = open(settings.ROOT_DIR + '/docs/modules/' + app.label + '.rst', 'w')
                            f_include.write(template_include_rendered)
                            f_include.close()
                            f.write(template_rendered)
    exit(0)
