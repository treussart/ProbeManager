import importlib
import logging

from django.apps.registry import apps
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from rules.models import Rule

logger = logging.getLogger(__name__)


@login_required
def search(request):
    """
    Search rules (Scripts and Signatures) from all the probes.
    """
    if request.GET.get("pattern"):
        pattern = request.GET.get("pattern")
        if pattern != "" and pattern != " ":
            data = list()
            for app in apps.get_app_configs():
                first = True
                for model in app.get_models():
                    if issubclass(model, Rule):
                        if app.verbose_name != "Rules":
                            if first:
                                first = False
                                probe_data = dict()
                                try:
                                    my_class = getattr(importlib.import_module(app.label + ".models"),
                                                       'Signature' + app.verbose_name)
                                    signatures = my_class.find(pattern)
                                    probe_data.update({'signatures': signatures})

                                    my_class = getattr(importlib.import_module(app.label + ".models"),
                                                       'Script' + app.verbose_name)
                                    scripts = my_class.find(pattern)
                                    probe_data.update({'scripts': scripts})

                                    my_class = getattr(importlib.import_module(app.label + ".models"),
                                                       'Rule' + app.verbose_name)
                                    rules = my_class.find(pattern)
                                    probe_data.update({'rules': rules})
                                except AttributeError:
                                    pass
                                probe_data.update({'name': app.label})
                                data.append(probe_data)
            return render(request, 'rules/search.html', {'data': data})
        else:
            return render(request, 'rules/search.html', {'message': 'Pattern ' + pattern + ' not found'})
    else:
        return render(request, 'rules/search.html', {'message': 'Pattern not found'})
