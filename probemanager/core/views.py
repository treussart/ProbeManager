import importlib
import json
import logging
import os

from django.apps.registry import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe

from .models import Probe
from .tasks import deploy_rules as deploy_rules_probe, install_probe, update_probe

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
                if app.verbose_name != "Core":
                    my_class = getattr(importlib.import_module(app.label + ".models"), app.verbose_name)
                    instances[app.label] = my_class.get_all()
    return render(request, 'core/index.html', {'instances': instances})


@login_required
def probe_index(request, pk):
    """
    Display an individual Probe instance.
    """
    probe = Probe.get_by_id(pk)
    if probe is None:
        return HttpResponseNotFound('<h1>Page not found</h1>')
    if probe.subtype:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.subtype)
    else:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.type)
    probe = my_class.get_by_id(pk)
    if probe is None:
        return HttpResponseNotFound('<h1>Page not found</h1>')
    else:
        return render(request, probe.type.lower() + '/index.html', {'probe': probe})


@login_required
def start(request, pk):
    """
    Start a probe instance.
    """
    probe = Probe.get_by_id(pk)
    if probe is None:
        return HttpResponseNotFound()
    if probe.subtype:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.subtype)
    else:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.type)
    probe = my_class.get_by_id(pk)
    try:
        response_start = probe.start()
        if response_start['status']:
            messages.add_message(request, messages.SUCCESS, 'Probe started successfully')
        else:
            messages.add_message(request, messages.ERROR,
                                 'Error during the start: ' + str(response_start['errors']))
    except Exception as e:
        logger.exception('Error during the start : ' + str(e))
        messages.add_message(request, messages.ERROR, 'Error during the start : ' + str(e))
    return render(request, probe.type.lower() + '/index.html', {'probe': probe})


@login_required
def stop(request, pk):
    """
    Stop a probe instance.
    """
    probe = Probe.get_by_id(pk)
    if probe is None:
        return HttpResponseNotFound()
    if probe.subtype:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.subtype)
    else:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.type)
    probe = my_class.get_by_id(pk)
    try:
        response_stop = probe.stop()
        if response_stop['status']:
            messages.add_message(request, messages.SUCCESS, 'Probe stopped successfully')
        else:
            messages.add_message(request, messages.ERROR, 'Error during the stop: ' + str(response_stop['errors']))
    except Exception as e:
        logger.exception('Error during the stop : ' + str(e))
        messages.add_message(request, messages.ERROR, 'Error during the stop : ' + str(e))
    return render(request, probe.type.lower() + '/index.html', {'probe': probe})


@login_required
def restart(request, pk):
    """
    Restart a probe instance.
    """
    probe = Probe.get_by_id(pk)
    if probe is None:
        return HttpResponseNotFound()
    if probe.subtype:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.subtype)
    else:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.type)
    probe = my_class.get_by_id(pk)
    try:
        response_restart = probe.restart()
        if response_restart['status']:
            messages.add_message(request, messages.SUCCESS, 'Probe restarted successfully')
        else:
            messages.add_message(request, messages.ERROR,
                                 'Error during the restart: ' + str(response_restart['errors']))
    except Exception as e:
        logger.exception('Error during the restart : ' + str(e))
        messages.add_message(request, messages.ERROR, 'Error during the restart : ' + str(e))
    return render(request, probe.type.lower() + '/index.html', {'probe': probe})


@login_required
def reload(request, pk):
    """
    Reload a probe instance.
    """
    probe = Probe.get_by_id(pk)
    if probe is None:
        return HttpResponseNotFound()
    if probe.subtype:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.subtype)
    else:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.type)
    probe = my_class.get_by_id(pk)
    try:
        response_reload = probe.reload()
        if response_reload['status']:
            messages.add_message(request, messages.SUCCESS, 'Probe reloaded successfully')
        else:
            messages.add_message(request, messages.ERROR,
                                 'Error during the reload: ' + str(response_reload['errors']))
    except Exception as e:
        logger.exception('Error during the reload : ' + str(e))
        messages.add_message(request, messages.ERROR, 'Error during the reload : ' + str(e))
    return render(request, probe.type.lower() + '/index.html', {'probe': probe})


@login_required
def status(request, pk):
    """
    Status of a probe instance.
    """
    probe = Probe.get_by_id(pk)
    if probe is None:
        return HttpResponseNotFound()
    if probe.subtype:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.subtype)
    else:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.type)
    probe = my_class.get_by_id(pk)
    try:
        response_status = probe.status()
        if response_status:
            messages.add_message(request, messages.SUCCESS,
                                 "OK probe " + str(probe.name) + " get status successfully")
        else:
            messages.add_message(request, messages.ERROR, 'Error during the status')
    except Exception as e:
        logger.exception('Error during the status : ' + str(e))
        messages.add_message(request, messages.ERROR, 'Error during the status : ' + str(e))
    return render(request, probe.type.lower() + '/index.html', {'probe': probe})


@login_required
def install(request, pk):
    """
    Install a probe instance.
    """
    probe = Probe.get_by_id(pk)
    if probe is None:
        return HttpResponseNotFound()
    if probe.subtype:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.subtype)
    else:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.type)
    probe = my_class.get_by_id(pk)
    try:
        install_probe.delay(probe.name)
    except Exception as e:
        logger.exception('Error during the install : ' + str(e))
        messages.add_message(request, messages.ERROR, 'Error during the install : ' + str(e))
    messages.add_message(request, messages.SUCCESS,
                         "Install probe launched with succeed. " +
                         mark_safe("<a href='/admin/core/job/'>View Job</a>"))
    return render(request, probe.type.lower() + '/index.html', {'probe': probe})


@login_required
def update(request, pk):
    """
    Update a probe instance.
    """
    probe = Probe.get_by_id(pk)
    if probe is None:
        return HttpResponseNotFound()
    if probe.subtype:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.subtype)
    else:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.type)
    probe = my_class.get_by_id(pk)
    try:
        update_probe.delay(probe.name)
    except Exception as e:
        logger.exception('Error during the update : ' + str(e))
        messages.add_message(request, messages.ERROR, 'Error during the update : ' + str(e))
    messages.add_message(request, messages.SUCCESS,
                         "Update probe launched with succeed. " +
                         mark_safe("<a href='/admin/core/job/'>View Job</a>"))
    return render(request, probe.type.lower() + '/index.html', {'probe': probe})


@login_required
def deploy_conf(request, pk):
    """
    Deploy the configuration of a probe instance.
    """
    probe = Probe.get_by_id(pk)
    if probe is None:
        return HttpResponseNotFound()
    if probe.subtype:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.subtype)
    else:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.type)
    probe = my_class.get_by_id(pk)
    response_test = probe.configuration.test()
    logger.debug(str(response_test))
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
        if response_deploy_conf['status'] and response_restart['status']:
            messages.add_message(request, messages.SUCCESS, 'Deployed configuration successfully')
        elif not response_deploy_conf['status']:
            messages.add_message(request, messages.ERROR,
                                 'Error during the configuration deployed: ' + str(response_deploy_conf['errors']))
        elif not response_restart['status']:
            messages.add_message(request, messages.ERROR,
                                 'Error during the configuration deployed: ' + str(response_restart['errors']))
    except Exception as e:
        logger.exception('Error during the configuration deployed : ' + str(e))
        messages.add_message(request, messages.ERROR, 'Error during the configuration deployed : ' + str(e))
    return render(request, probe.type.lower() + '/index.html', {'probe': probe})


@login_required
def deploy_rules(request, pk):
    """
    Deploy the rules of a probe instance.
    """
    probe = Probe.get_by_id(pk)
    if probe is None:
        return HttpResponseNotFound()
    if probe.subtype:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.subtype)
    else:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.type)
    probe = my_class.get_by_id(pk)
    try:
        deploy_rules_probe.delay(probe.name)
        messages.add_message(request, messages.SUCCESS,
                             "Deployed rules launched with succeed. " +
                             mark_safe("<a href='/admin/core/job/'>View Job</a>"))
    except Exception as e:
        logger.exception('Error during the rules deployment : ' + str(e))
        messages.add_message(request, messages.ERROR, 'Error during the rules deployment : ' + str(e))
    return render(request, probe.type.lower() + '/index.html', {'probe': probe})
