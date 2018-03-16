from core.utils import encrypt
from jinja2 import Template
from getpass import getpass
import sys

template_smtp = """
['EMAIL']
EMAIL_HOST = {{ host }}
EMAIL_PORT = {{ port }}
EMAIL_HOST_USER = {{ host_user }}
EMAIL_HOST_PASSWORD = {{ password }}
DEFAULT_FROM_EMAIL = {{ default_from_email }}
EMAIL_USE_TLS = {{ use_tls }}
"""


def run(*args):
    print("Server SMTP :")
    host = input('host : ')
    port = input('port : ')
    host_user = input('user : ')
    host_password = getpass('password : ')
    default_from_email = input('default from email : ')
    use_tls = input('The SMTP host use TLS ? : (True/False) ')

    t = Template(template_smtp)
    final = t.render(host=host,
                     port=port,
                     host_user=host_user,
                     default_from_email=default_from_email,
                     use_tls=str(use_tls),
                     password=encrypt(host_password).decode('utf-8')
                     )

    with open(args[0] + 'conf.ini', 'a', encoding='utf_8') as f:
        f.write(final)
    sys.exit(0)
