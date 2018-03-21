import argparse
import sys
from getpass import getpass

from cryptography.fernet import Fernet
from jinja2 import Template

template_smtp = """
[EMAIL]
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
    return fernet_key.encrypt(plain_text.encode('utf-8')).decode('utf-8')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dest", help="", default='/etc/')
    args = parser.parse_args()
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

    with open(args.dest + 'conf.ini', 'a', encoding='utf_8') as f:
        f.write(final)
    with open(args.dest + 'password_email.txt', 'w', encoding='utf_8') as f:
        f.write(encrypt(host_password, args.dest))
    sys.exit(0)
