import os
from string import Template

from probemanager.settings.prod import APACHE_PORT, PROJECT_NAME


def generate_apache_conf(project_name, dest, port):
    template_conf = """
WSGIPythonHome ${dest}/venv
WSGIPythonPath ${dest}/${project_name}

<VirtualHost *:${port}>

    Alias /static/ ${dest}/${project_name}/static/

    <Directory ${dest}/${project_name}/static>
    Require all granted
    </Directory>

    Alias /docs/ ${dest}/docs/_build/html/

    <Directory "${dest}/docs/_build/html">
    Require all granted
    </Directory>

    WSGIScriptAlias / ${dest}/${project_name}/${project_name}/wsgi.py
    SetEnv DJANGO_SETTINGS_MODULE ${dest}/${project_name}/${project_name}/settings/prod.py

    LogFormat "%v %h %l %u %t \\"%r\\" %>s %b" serveur_virtuel_commun
    CustomLog         /var/log/apache2/${project_name}-access.log serveur_virtuel_commun
    ErrorLog          /var/log/apache2/${project_name}-error.log

    <Directory ${dest}/${project_name}/${project_name}>
    <Files wsgi.py>
    Require all granted
    </Files>
    </Directory>

</VirtualHost>
"""
    t = Template(template_conf)
    apache_conf = t.safe_substitute(project_name=project_name, dest=dest, port=port)
    if os.path.isdir('/etc/apache2/sites-enabled/'):
        install_dir = '/etc/apache2/sites-enabled/'
    else:
        install_dir = dest
    with open(install_dir + 'probemanager.conf', 'w') as f:
        f.write(apache_conf)


def run(*args):
    dest = args[0].rstrip('/')
    port = APACHE_PORT
    generate_apache_conf(PROJECT_NAME, dest, port)
    exit()
