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
from home.tasks import deploy_rules as deploy_rules_probe, install_probe, update_probe


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
        try:
            response_start = probe.start()
            if response_start:
                messages.add_message(request, messages.SUCCESS, 'Probe started successfully')
            else:
                messages.add_message(request, messages.ERROR, 'Error during the start')
        except Exception as e:
            messages.add_message(request, messages.ERROR, 'Error during the start : ' + e.__str__())
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
        try:
            response_stop = probe.stop()
            if response_stop:
                messages.add_message(request, messages.SUCCESS, 'Probe stopped successfully')
            else:
                messages.add_message(request, messages.ERROR, 'Error during the stop')
        except Exception as e:
            messages.add_message(request, messages.ERROR, 'Error during the stop : ' + e.__str__())
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
        try:
            response_restart = probe.restart()
            if response_restart:
                messages.add_message(request, messages.SUCCESS, 'Probe restarted successfully')
            else:
                messages.add_message(request, messages.ERROR, 'Error during the restart')
        except Exception as e:
            messages.add_message(request, messages.ERROR, 'Error during the restart : ' + e.__str__())
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
        try:
            response_reload = probe.reload()
            if response_reload:
                messages.add_message(request, messages.SUCCESS, 'Probe reloaded successfully')
            else:
                messages.add_message(request, messages.ERROR, 'Error during the reload')
        except Exception as e:
            messages.add_message(request, messages.ERROR, 'Error during the reload : ' + e.__str__())
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
        try:
            response_status = probe.status()
            if response_status:
                messages.add_message(request, messages.SUCCESS, "OK probe " + str(probe.name) + " get status successfully")
            else:
                messages.add_message(request, messages.ERROR, 'Error during the status')
        except Exception as e:
            messages.add_message(request, messages.ERROR, 'Error during the status : ' + e.__str__())
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
        try:
            install_probe.delay(probe.name)
        except Exception as e:
            messages.add_message(request, messages.ERROR, 'Error during the install : ' + e.__str__())
        messages.add_message(request, messages.SUCCESS, 'Install probe launched with succeed. View Job')
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
        try:
            update_probe.delay(probe.name)
        except Exception as e:
            messages.add_message(request, messages.ERROR, 'Error during the update : ' + e.__str__())
        messages.add_message(request, messages.SUCCESS, 'Update probe launched with succeed. View Job')
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
        try:
            response_deploy_conf = probe.deploy_conf()
            response_restart = probe.restart()
            if response_deploy_conf and response_restart:
                messages.add_message(request, messages.SUCCESS, 'Deployed configuration successfully')
            else:
                messages.add_message(request, messages.ERROR, 'Error during the configuration deployed')
        except Exception as e:
            messages.add_message(request, messages.ERROR, 'Error during the configuration deployed : ' + e.__str__())
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
        try:
            deploy_rules_probe.delay(probe.name)
        except Exception as e:
            messages.add_message(request, messages.ERROR, 'Error during the install : ' + e.__str__())
        messages.add_message(request, messages.SUCCESS, 'Deployed rules launched with succeed. View Job')
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
