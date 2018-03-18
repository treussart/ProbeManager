from jinja2 import Template
from getpass import getpass
import sys
from cryptography.fernet import Fernet


template_smtp = """
['EMAIL']
EMAIL_HOST = {{ host }}
EMAIL_PORT = {{ port }}
EMAIL_HOST_USER = {{ host_user }}
DEFAULT_FROM_EMAIL = {{ default_from_email }}
EMAIL_USE_TLS = {{ use_tls }}
"""


def encrypt(plain_text, dest):
    with open(dest + 'fernet_key.txt') as f:
        fernet_key_bytes = bytes(f.read().strip(), 'utf-8')
    fernet_key = Fernet(fernet_key_bytes)
    return fernet_key.encrypt(plain_text.encode('utf-8'))


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
                     use_tls=str(use_tls)
                     )

    with open(args[0] + 'conf.ini', 'a', encoding='utf_8') as f:
        f.write(final)
    with open(args[0] + 'password_email.txt', 'w', encoding='utf_8') as f:
        f.write(encrypt(host_password, args[0]).decode('utf-8'))
    sys.exit(0)
