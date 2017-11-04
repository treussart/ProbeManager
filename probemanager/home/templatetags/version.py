from django import template
from django.conf import settings
import os


register = template.Library()


@register.simple_tag
def version(app):
    if app == 'ProbeManager':
        with open(os.path.join(settings.BASE_DIR + '/version.txt')) as f:
            return f.read().strip()
    else:
        with open(os.path.join(settings.BASE_DIR + "/" + app['app_label'] + '/version.txt')) as f:
            return f.read().strip()


@register.filter
def test_version(app):
    if os.path.isfile(os.path.join(settings.BASE_DIR + "/" + app['app_label'] + '/version.txt')):
        return True
    else:
        return False
