from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.apps.registry import apps
from home.models import Probe
import importlib
from django.http import HttpResponseNotFound
from django.contrib import messages
import os
from django.http import JsonResponse
from django.conf import settings
import json
import logging


logger = logging.getLogger(__name__)


@login_required
def index(request):
    """
    Display all probes instances.
    """
    instances = dict()
    for app in apps.get_app_configs():
        for model in app.get_models():
            if issubclass(model, Probe):
                if app.verbose_name != "Home":
                    my_class = getattr(importlib.import_module(app.label + ".models"), app.verbose_name)
                    instances[app.label] = my_class.get_all()
    return render(request, 'home/index.html', {'instances': instances})


@login_required
def probe_index(request, id):
    """
    Display an individual Probe instance.
    """
    probe = Probe.get_by_id(id)
    my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.type)
    probe = my_class.get_by_id(id)
    if probe is None:
        return HttpResponseNotFound('<h1>Page not found</h1>')
    else:
        return render(request, probe.type.lower() + '/index.html', {'probe': probe})


@login_required
def start(request, id):
    """
    Start a probe instance.
    """
    probe = Probe.get_by_id(id)
    my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.type)
    probe = my_class.get_by_id(id)
    if probe is None:
        return HttpResponseNotFound
    else:
        response_start = probe.start()
        if response_start['result'] == 0:
            messages.add_message(request, messages.SUCCESS, 'Started successfully')
        else:
            messages.add_message(request, messages.ERROR, 'Error during the start')
        return render(request, probe.type.lower() + '/index.html', {'probe': probe})


@login_required
def stop(request, id):
    """
    Stop a probe instance.
    """
    probe = Probe.get_by_id(id)
    my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.type)
    probe = my_class.get_by_id(id)
    if probe is None:
        return HttpResponseNotFound
    else:
        response_stop = probe.stop()
        if response_stop['result'] == 0:
            messages.add_message(request, messages.SUCCESS, 'Stopped successfully')
        else:
            messages.add_message(request, messages.ERROR, 'Error during the stop')
        return render(request, probe.type.lower() + '/index.html', {'probe': probe})


@login_required
def restart(request, id):
    """
    Restart a probe instance.
    """
    probe = Probe.get_by_id(id)
    my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.type)
    probe = my_class.get_by_id(id)
    if probe is None:
        return HttpResponseNotFound
    else:
        response_restart = probe.restart()
        if response_restart['result'] == 0:
            messages.add_message(request, messages.SUCCESS, 'Restarted successfully')
        else:
            messages.add_message(request, messages.ERROR, 'Error during the restart')
        return render(request, probe.type.lower() + '/index.html', {'probe': probe})


@login_required
def reload(request, id):
    """
    Reload a probe instance.
    """
    probe = Probe.get_by_id(id)
    my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.type)
    probe = my_class.get_by_id(id)
    if probe is None:
        return HttpResponseNotFound
    else:
        response_reload = probe.reload()
        if response_reload['result'] == 0:
            messages.add_message(request, messages.SUCCESS, 'Reloaded successfully')
        else:
            messages.add_message(request, messages.ERROR, 'Error during the reload')
        return render(request, probe.type.lower() + '/index.html', {'probe': probe})


@login_required
def status(request, id):
    """
    Status of a probe instance.
    """
    probe = Probe.get_by_id(id)
    my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.type)
    probe = my_class.get_by_id(id)
    if probe is None:
        return HttpResponseNotFound
    else:
        probe.status()
        return render(request, probe.type.lower() + '/index.html', {'probe': probe})


@login_required
def install(request, id):
    """
    Install a probe instance.
    """
    probe = Probe.get_by_id(id)
    my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.type)
    probe = my_class.get_by_id(id)
    if probe is None:
        return HttpResponseNotFound
    else:
        response_install = probe.install()
        probe.deploy_conf()
        probe.deploy_rules()
        response_start = probe.start()
        if response_install['result'] == 0 and response_start['result'] == 0:
            messages.add_message(request, messages.SUCCESS, 'Installed successfully')
        else:
            messages.add_message(request, messages.ERROR, 'Error during the install')
        return render(request, probe.type.lower() + '/index.html', {'probe': probe})


@login_required
def update(request, id):
    """
    Update a probe instance.
    """
    probe = Probe.get_by_id(id)
    my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.type)
    probe = my_class.get_by_id(id)
    if probe is None:
        return HttpResponseNotFound
    else:
        response_update = probe.update()
        response_restart = probe.restart()
        if response_update['result'] == 0 and response_restart['result'] == 0:
            messages.add_message(request, messages.SUCCESS, 'Updated successfully')
        else:
            messages.add_message(request, messages.ERROR, 'Error during the update')
        return render(request, probe.type.lower() + '/index.html', {'probe': probe})


@login_required
def deploy_conf(request, id):
    """
    Deploy the configuration of a probe instance.
    """
    probe = Probe.get_by_id(id)
    my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.type)
    probe = my_class.get_by_id(id)
    if probe is None:
        return HttpResponseNotFound
    else:
        response_test = probe.configuration.test()
        logger.error(str(response_test))
        if probe.secure_deployment:
            if not response_test['status']:
                messages.add_message(request, messages.ERROR, 'Error during the test configuration')
                return render(request, probe.type.lower() + '/index.html', {'probe': probe})
        if response_test['status']:
            messages.add_message(request, messages.SUCCESS, "Test configuration OK")
        else:
            messages.add_message(request, messages.ERROR, "Test configuration failed ! " + str(response_test['errors']))
        response_deploy_conf = probe.deploy_conf()
        response_restart = probe.restart()
        if response_deploy_conf['result'] == 0 and response_restart['result'] == 0:
            messages.add_message(request, messages.SUCCESS, 'Deployed configuration successfully')
        else:
            messages.add_message(request, messages.ERROR, 'Error during the configuration deployed')
        return render(request, probe.type.lower() + '/index.html', {'probe': probe})


@login_required
def deploy_rules(request, id):
    """
    Deploy the rules of a probe instance.
    """
    probe = Probe.get_by_id(id)
    my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.type)
    probe = my_class.get_by_id(id)
    if probe is None:
        return HttpResponseNotFound
    else:
        response_tests = probe.test_rules()
        test_pcap = True
        errors = list()
        if probe.secure_deployment:
            if not response_tests['status']:
                messages.add_message(request, messages.ERROR, 'Error during the rules test')
                return render(request, probe.type.lower() + '/index.html', {'probe': probe})
            elif not test_pcap:
                messages.add_message(request, messages.ERROR, "Test pcap failed ! " + str(errors))
                return render(request, probe.type.lower() + '/index.html', {'probe': probe})
        if response_tests['status']:
            messages.add_message(request, messages.SUCCESS, "Test signatures OK")
        else:
            messages.add_message(request, messages.ERROR, "Test signatures failed ! " + str(response_tests['errors']))
        if test_pcap:
            messages.add_message(request, messages.SUCCESS, "Test pcap OK")
        else:
            messages.add_message(request, messages.ERROR, "Test pcap failed ! " + str(errors))
        response_deploy_rules = probe.deploy_rules()
        response_reload = probe.reload()
        if response_deploy_rules['result'] == 0 and response_reload['result'] == 0:
            messages.add_message(request, messages.SUCCESS, 'Deployed rules successfully')
        else:
            messages.add_message(request, messages.ERROR, 'Error during the rules deployed')
        return render(request, probe.type.lower() + '/index.html', {'probe': probe})


def get_progress(request):
    """
    Get the progress value for the progress bar.
    """
    if os.path.isfile(settings.BASE_DIR + '/tmp/progress.json'):
        f = open(settings.BASE_DIR + "/tmp/progress.json", 'r')
        return JsonResponse(json.loads(f.read()))
    else:
        return JsonResponse({'progress': 0})
