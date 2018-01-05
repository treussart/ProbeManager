from celery import task
from celery.utils.log import get_task_logger
from home.models import Probe, Job
from suricata.models import RuleSetSuricata
import importlib
from rules.models import Source
from home.notifications import send_notification
import traceback


logger = get_task_logger(__name__)


@task
def deploy_rules(probe_name):
    job = Job.create_job('deploy_rules', probe_name)
    probe = Probe.get_by_name(probe_name)
    if probe is None:
        job.update_job("Error - probe is None - param id not set : " + str(probe_name), 'Error')
        return {"message": "Error - probe is None - param id not set : " + str(probe_name)}
    if probe.subtype:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.subtype)
    else:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.type)
    probe = my_class.get_by_name(probe_name)
    try:
        response_deploy_rules = probe.deploy_rules()
        response_reload = probe.reload()
        if response_deploy_rules['status'] and response_reload['status']:
            job.update_job('Deployed rules successfully', 'Completed')
        elif not response_deploy_rules['status']:
            job.update_job('Error during the rules deployed', 'Error: ' + str(probe_name) + " - " + str(response_deploy_rules['errors']))
            logger.error("task - deploy_rules : " + str(probe_name) + " - " + str(response_deploy_rules['errors']))
        elif not response_reload['status']:
            job.update_job('Error during the rules deployed', 'Error: ' + str(probe_name) + str(response_reload['errors']))
            logger.error("task - deploy_rules : " + str(probe_name) + " - " + str(response_reload['errors']))
    except Exception as e:
        logger.error(e.__str__())
        logger.error(traceback.print_exc())
        job.update_job(e.__str__(), 'Error')
        send_notification("Probe " + str(probe.name), e.__str__())
        return {"message": "Error for probe " + str(probe.name) + " to deploy rules", "exception": e.__str__()}
    return str(response_deploy_rules['message']) + " - " + str(response_reload['message'])


@task
def reload_probe(probe_name):
    job = Job.create_job('reload_probe', probe_name)
    probe = Probe.get_by_name(probe_name)
    if probe is None:
        job.update_job("Error - probe is None - param id not set : " + str(probe_name), 'Error')
        return {"message": "Error - probe is None - param id not set : " + str(probe_name)}
    if probe.subtype:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.subtype)
    else:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.type)
    probe = my_class.get_by_name(probe_name)
    if probe.scheduled_rules_deployment_enabled:
        try:
            response = probe.reload()
            if response['status']:
                job.update_job("task - reload_probe : " + str(probe_name), 'Completed')
                logger.info("task - reload_probe : " + str(probe_name))
                return {"message": "Probe " + str(probe.name) + "reloaded successfully"}
            else:
                job.update_job(str(response['errors']), 'Error')
                return {"message": "Error for probe " + str(probe.name) + " to reload", "exception": str(response['errors'])}
        except Exception as e:
            logger.error(e.__str__())
            logger.error(traceback.print_exc())
            job.update_job(e.__str__(), 'Error')
            send_notification("Probe " + str(probe.name), e.__str__())
            return {"message": "Error for probe " + str(probe.name) + " to reload", "exception": e.__str__()}
    else:
        job.update_job("Not enabled to reload", 'Error')
        send_notification("Probe " + str(probe.name), "Not enabled to reload")
        return {"message": probe.name + " not enabled to reload"}


@task
def upload_url_http(source_uri, rulesets_id=None):
    job = Job.create_job('upload_url_http', source_uri)
    rulesets = list()
    if rulesets_id:
        for ruleset_id in rulesets_id:
            rulesets.append(RuleSetSuricata.get_by_id(ruleset_id))
    try:
        source = Source.get_by_uri(source_uri)
        if source is None:
            job.update_job("Error - source is None - param id not set : " + str(source_uri), 'Error')
            return {"message": "Error - source is None - param id not set : " + str(source_uri)}
        my_class = getattr(importlib.import_module(source.type.lower().split('source')[1] + ".models"), source.type)
        source = my_class.get_by_uri(source_uri)
    except Exception as e:
        logger.error(e.__str__())
        logger.error(traceback.print_exc())
        job.update_job(e.__str__(), 'Error')
        return {"message": "Error for source to upload", "exception": e.__str__()}
    try:
        message = source.upload(rulesets)
        job.update_job(message, 'Completed')
        logger.info("task - upload_url_http : " + str(source_uri) + " - " + str(message))
    except Exception as e:
        logger.error(e.__str__())
        logger.error(traceback.print_exc())
        job.update_job(e.__str__(), 'Error')
        send_notification("Error for source " + str(source.uri), e.__str__())
        return {"message": "Error for source " + str(source.uri) + " to upload", "exception": e.__str__()}
    return {"message": "OK source " + str(source.uri) + " upload by HTTP", "upload_message": message}


@task
def install_probe(probe_name):
    job = Job.create_job('install_probe', probe_name)
    probe = Probe.get_by_name(probe_name)
    if probe is None:
        job.update_job("Error - probe is None - param id not set : " + str(probe_name), 'Error')
        return {"message": "Error - probe is None - param id not set : " + str(probe_name)}
    if probe.subtype:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.subtype)
    else:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.type)
    probe = my_class.get_by_name(probe_name)
    try:
        response_install = probe.install()
        response_deploy_conf = probe.deploy_conf()
        response_deploy_rules = probe.deploy_rules()
        response_start = probe.start()
    except Exception as e:
        logger.error(e.__str__())
        logger.error(traceback.print_exc())
        job.update_job(e.__str__(), 'Error')
        send_notification("Error for probe " + str(probe.name), e.__str__())
        return {"message": "Error for probe " + str(probe.name) + " to install", "exception": e.__str__()}
    if response_install['status'] and response_start['status'] and response_deploy_conf['status'] and response_deploy_rules['status']:
        job.update_job('Probe ' + str(probe.name) + ' installed successfully', 'Completed')
        return {"message": "OK probe " + str(probe.name) + " installed successfully"}
    else:
        job.update_job("Error for probe " + str(probe.name) + " to install", 'Error')
        return {"message": "Error for probe " + str(probe.name) + " to install"}


@task
def update_probe(probe_name):
    job = Job.create_job('update_probe', probe_name)
    probe = Probe.get_by_name(probe_name)
    if probe is None:
        job.update_job("Error - probe is None - param id not set : " + str(probe_name), 'Error')
        return {"message": "Error - probe is None - param id not set : " + str(probe_name)}
    if probe.subtype:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.subtype)
    else:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.type)
    probe = my_class.get_by_name(probe_name)
    try:
        response_update = probe.update()
        response_restart = probe.restart()
    except Exception as e:
        logger.error(e.__str__())
        logger.error(traceback.print_exc())
        job.update_job(e.__str__(), 'Error')
        send_notification("Error for probe " + str(probe.name), e.__str__())
        return {"message": "Error for probe " + str(probe.name) + " to install", "exception": e.__str__()}
    if response_update['status'] and response_restart['status']:
        job.update_job(response_update + response_restart, 'Completed')
        return {"message": "OK probe " + str(probe.name) + " updated successfully"}
    else:
        job.update_job("Error for probe " + str(probe.name) + " to update", 'Error')
        return {"message": "Error for probe " + str(probe.name) + " to update"}


@task
def check_probe(probe_name):
    job = Job.create_job('check_probe', probe_name)
    probe = Probe.get_by_name(probe_name)
    if probe is None:
        job.update_job("Error - probe is None - param id not set : " + str(probe_name), 'Error')
        return {"message": "Error - probe is None - param id not set : " + str(probe_name)}
    if probe.subtype:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.subtype)
    else:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.type)
    probe = my_class.get_by_name(probe_name)
    try:
        response_status = probe.status()
    except Exception as e:
        logger.error(e.__str__())
        logger.error(traceback.print_exc())
        job.update_job(e.__str__(), 'Error')
        send_notification("Error for probe " + str(probe.name), e.__str__())
        return {"message": "Error for probe " + str(probe.name) + " to check status", "exception": e.__str__()}
    if response_status:
        if 'active (running)' in response_status:
            job.update_job("OK probe " + str(probe.name) + " is running", 'Completed')
            return {"message": "OK probe " + str(probe.name) + " is running"}
        else:
            job.update_job("KO probe " + str(probe.name) + " is not running", 'Completed')
            send_notification("probe KO", "Probe " + str(probe.name) + " is not running")
            return {"message": "KO probe " + str(probe.name) + " is not running"}
    else:
        job.update_job("Error for probe " + str(probe.name) + " to check status", 'Error')
        return {"message": "Error for probe " + str(probe.name) + " to check status"}
