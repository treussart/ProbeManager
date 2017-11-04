from .celery import app as celery_app
import platform
import sys
import warnings


if not (3) <= sys.version_info[0]:
    sys.exit(
        'ERROR: Probe Manager requires Python 3, but found %s.' %
        platform.python_version())

warnings.filterwarnings('ignore', 'could not open display')


__all__ = ['celery_app']
__author__ = 'TREUSSART Matthieu'
__author_email__ = 'matthieu@treussart.com'
__title__ = 'Probe Manager'
__licence__ = 'GNU GPLv3'
