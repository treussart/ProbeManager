from probemanager.settings.base import *
from cryptography.fernet import Fernet
import configparser
import ast
import os
import importlib


assert importlib


config = configparser.ConfigParser()
config.read(os.path.join(GIT_ROOT, 'conf.ini'))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

HOST = config['DEFAULT']['HOST']
ALLOWED_HOSTS = [HOST, 'localhost', '127.0.0.1']
GIT_BINARY = config['GIT']['GIT_BINARY']

# Specific for installation
PROJECT_NAME = 'probemanager'
APACHE_PORT = 80

with open(os.path.join(GIT_ROOT, 'secret_key.txt')) as f:
    SECRET_KEY = f.read().strip()
with open(os.path.join(GIT_ROOT, 'fernet_key.txt')) as f:
    FERNET_KEY = bytes(f.read().strip(), 'utf-8')

if os.path.isfile(os.path.join(BASE_DIR, 'version.txt')):
    with open(os.path.join(BASE_DIR, 'version.txt')) as f:
        VERSION = f.read().strip()
else:
    VERSION = ""

def decrypt(cipher_text):
    fernet_key = Fernet(FERNET_KEY)
    if isinstance(cipher_text, bytes):
        return fernet_key.decrypt(cipher_text).decode('utf-8')
    else:
        return fernet_key.decrypt(bytes(cipher_text, 'utf-8'))


with open(os.path.join(GIT_ROOT, 'password_db.txt')) as f:
    PASSWORD_DB = decrypt(bytes(f.read().strip(), 'utf-8'))

# Celery settings
CELERY_BROKER_URL = 'amqp://guest:guest@localhost//'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
    },
    'formatters': {
        'simple': {
            'format': '%(asctime)s %(levelname)s %(name)s %(funcName)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'simple',
            # 'filename': os.path.join(tempfile.gettempdir(), 'probemanager-debug.log'),
            'filename': os.path.join(BASE_DIR, 'probemanager.log'),
            'filters': ['require_debug_false']
        },
    },
    'loggers': {
        'django': {
            'handlers': ['mail_admins', 'file'],
            'level': 'INFO',
            'formatter': 'simple'
        },
        'django.template': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['mail_admins'],
            'level': 'INFO',
            'formatter': 'simple',
            'propagate': True
        },
        'django.db.backends': {
            'handlers': ['file'],
            'level': 'INFO',
            'formatter': 'simple',
            'propagate': True
        },
        'home': {
            'handlers': ['file'],
            'level': 'INFO',
            'formatter': 'simple',
            'propagate': True
        },
        'rules': {
            'handlers': ['file'],
            'level': 'INFO',
            'formatter': 'simple',
            'propagate': True
        },
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'probemanager',
        'USER': 'probemanager',
        'PASSWORD': PASSWORD_DB,
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

PROD_APPS = ast.literal_eval(config['APPS']['PROD_APPS'])
INSTALLED_APPS = BASE_APPS + PROD_APPS

for app in PROD_APPS:
    LOGGING['loggers'].update({app: {'handlers': ['file'], 'level': 'INFO', 'formatter': 'simple', 'propagate': True}})
    if os.path.isfile(BASE_DIR + "/" + app + "/settings.py"):
        exec(open(BASE_DIR + "/" + app + "/settings.py").read())


# SMTP
EMAIL_SUBJECT_PREFIX = '[ProbeManager]'
EMAIL_HOST = config['EMAIL']['HOST']
EMAIL_HOST_USER = config['EMAIL']['USER']
with open(os.path.join(GIT_ROOT, 'password_email.txt')) as f:
    EMAIL_HOST_PASSWORD = decrypt(f.read().strip())
DEFAULT_FROM_EMAIL = config['EMAIL']['FROM']
EMAIL_USE_TLS = config.getboolean('EMAIL', 'TLS')

TIME_ZONE = config['DEFAULT']['TIME_ZONE']
