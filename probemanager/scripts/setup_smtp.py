from home.utils import encrypt
from jinja2 import Template
from getpass import getpass
import sys

template_smtp = """
EMAIL_HOST = '{{ host }}'
EMAIL_HOST_USER = '{{ host_user }}'
EMAIL_HOST_PASSWORD = decrypt('{{ host_password }}')
DEFAULT_FROM_EMAIL = '{{ default_from_email }}'
EMAIL_USE_TLS = {{ use_tls }}
"""


def run(*args):
    skip = input('Skip SMTP settings ? (Y/n) ')
    if skip.lower() == 'y' or not skip:
        sys.exit(0)
    else:
        print("Server SMTP :")
        host = input('host : ')
        host_user = input('user : ')
        host_password = getpass('password : ')
        default_from_email = input('default from email : ')
        use_tls = input('The SMTP host use TLS ? : (True/False) ')

        t = Template(template_smtp)
        final = t.render(host=host,
                         host_user=host_user,
                         host_password=encrypt(host_password).decode('utf-8'),
                         default_from_email=default_from_email,
                         use_tls=str(use_tls)
                         )

        with open(args[0] + 'probemanager/probemanager/settings/prod.py', 'a') as f:
            f.write(final)
        f.close()
        sys.exit(0)
