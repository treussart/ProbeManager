from django.apps.registry import apps
from jinja2 import Template
from home.models import Probe
import os
import sys
from django.conf import settings
from sphinx import main


def run(*args):
    #  from django.core.management import call_command
    #  call_command('graph_models suricata rules home -g -o docs/data/models_probemanager.png --settings=probemanager.settings.$arg')
    # Create index file  problem works without (solution le mettre dans script install.sh)
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
    with open(settings.GIT_ROOT + '/docs/modules/index.rst', 'w') as f:
        for app in apps.get_app_configs():
            for model in app.get_models():
                if issubclass(model, Probe):
                    if app.verbose_name != "Home":
                        path = settings.BASE_DIR + "/" + app.label + "/README.rst"
                        if os.path.isfile(path):
                            template_rendered = t.render(module=app.label, name=app.verbose_name)
                            template_include_rendered = t_include.render(module=app.label)
                            f_include = open(settings.GIT_ROOT + '/docs/modules/' + app.label + '.rst', 'w')
                            f_include.write(template_include_rendered)
                            f_include.close()
                            f.write(template_rendered)
    if args[0] != "-":
        dest = args[0].rstrip('/')
        sys.exit(main(["-b html", dest + "/docs", dest + "/docs/_build/html"]))
    else:
        sys.exit(main(["-b html", settings.GIT_ROOT + "/docs", settings.GIT_ROOT + "/docs/_build/html"]))

