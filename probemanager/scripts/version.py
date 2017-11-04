import sys
from django.apps.registry import apps
from django.conf import settings
from home.git import git_tag
from home.models import Probe


def run(*args):
    if args[0] != "-":
        dest = args[0].rstrip('/') + '/probemanager'
        if args[1]:
            source = args[1] + '/probemanager'
    else:
        dest = settings.BASE_DIR
        source = settings.BASE_DIR
    # en prod git_tag prendre des sources ou copier git_root = settings.BASE_DIR
    with open(dest + '/version.txt', 'w') as f:
        f.write(git_tag(source))
    f.close()
    for app in apps.get_app_configs():
        for model in app.get_models():
            if issubclass(model, Probe):
                if app.verbose_name != "Home":
                    dest_app = dest + "/" + app.label + '/'
                    source_app = source + "/" + app.label + '/'
                    with open(dest_app + 'version.txt', 'w') as f:
                        f.write(git_tag(source_app))
    sys.exit(0)
