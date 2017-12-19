from home.utils import encrypt
from jinja2 import Template
from getpass import getpass
import sys

template_smtp = """
[EMAIL]
HOST = {{ host }}
USER = {{ host_user }}
FROM = {{ default_from_email }}
TLS = {{ use_tls }}
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
                         default_from_email=default_from_email,
                         use_tls=str(use_tls)
                         )

        with open(args[0] + 'conf.ini', 'a') as f:
            f.write(final)
        f.close()
        with open(args[0] + 'password_email.txt', 'w') as f:
            f.write(encrypt(host_password).decode('utf-8'))
        f.close()
        sys.exit(0)
