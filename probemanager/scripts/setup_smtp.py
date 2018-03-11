from home.utils import encrypt
from jinja2 import Template
from getpass import getpass
import sys

template_smtp = """

#SMTP
EMAIL_HOST = {{ host }}
EMAIL_PORT = {{ port }}
EMAIL_HOST_USER = {{ host_user }}
DEFAULT_FROM_EMAI = {{ default_from_email }}
EMAIL_USE_TLS = {{ use_tls }}
with open(os.path.join(ROOT_DIR, 'password_email.txt'), encoding='utf_8') as f:
    EMAIL_HOST_PASSWORD = decrypt(f.read().strip())

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
                     use_tls=str(use_tls)
                     )

    with open(args[0] + 'probemanager/probemanager/settings/prod.py', 'a', encoding='utf_8') as f:
        f.write(final)
    with open(args[0] + 'password_email.txt', 'w', encoding='utf_8') as f:
        f.write(encrypt(host_password).decode('utf-8'))
    sys.exit(0)
