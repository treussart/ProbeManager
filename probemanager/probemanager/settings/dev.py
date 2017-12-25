from probemanager.settings.base import *
from home.git import git_tag
import configparser
import os
import importlib


assert importlib

config = configparser.ConfigParser()
config.read(os.path.join(GIT_ROOT, 'conf.ini'))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['*']

SECRET_KEY = 'j-93#)n%t8d0%tyo$f2e+$!%5-#wj65d#85@9y8jf)%_69_1ek'
FERNET_KEY = b'ly8WTzGyN6Xz23t5yq_s_1Ob-qmccqdi52Baj4ta_qQ='

GIT_BINARY = config['GIT']['GIT_BINARY']

VERSION = git_tag(GIT_ROOT)

# Celery settings
CELERY_BROKER_URL = 'amqp://guest:guest@localhost//'

TIME_ZONE = 'UTC'

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
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'simple',
            # 'filename': os.path.join(tempfile.gettempdir(), 'probemanager-debug.log'),
            'filename': os.path.join(BASE_DIR, 'probemanager.log'),
            'filters': ['require_debug_false']
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'filters': ['require_debug_true']
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'formatter': 'simple'
        },
        'django.template': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'formatter': 'simple',
            'propagate': True
        },
        'django.db.backends': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'formatter': 'simple',
            'propagate': True
        },
        'home': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'formatter': 'simple',
            'propagate': True
        },
        'rules': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'formatter': 'simple',
            'propagate': True
        },
    },

}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'probemanager',
        'USER': 'probemanager',
        'PASSWORD': 'probemanager',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

DEV_APPS = ['suricata', 'checkcve', 'ossec']
INSTALLED_APPS = BASE_APPS + DEV_APPS

for app in DEV_APPS:
    LOGGING['loggers'].update({app: {'handlers': ['console', 'file'], 'level': 'DEBUG', 'formatter': 'simple', 'propagate': True}})
    if os.path.isfile(BASE_DIR + "/" + app + "/settings.py"):
        exec(open(BASE_DIR + "/" + app + "/settings.py").read())

