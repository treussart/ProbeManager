from celery import task
from celery.utils.log import get_task_logger
from home.models import Probe, Job
from suricata.models import RuleSetSuricata
import importlib
from rules.models import Source
from home.utils import send_notification
import traceback


logger = get_task_logger(__name__)


""" Ansible code return :
RUN_OK = 0
RUN_ERROR = 1
RUN_FAILED_HOSTS = 2
RUN_UNREACHABLE_HOSTS = 4
RUN_FAILED_BREAK_PLAY = 8
RUN_UNKNOWN_ERROR = 255
"""


@task
def deploy_rules(probe_name):
    job = Job.create_job('deploy_rules', probe_name)
    probe = Probe.get_by_name(probe_name)
    if probe is None:
        return {"message": "Error - probe is None - param id not set : " + str(probe_name)}
    my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.type)
    probe = my_class.get_by_name(probe_name)
    try:
        message = probe.deploy_rules()
        job.update_job(message, 'Completed')
        logger.info("task - deploy_rules : " + str(probe_name) + " - " + str(message))
    except Exception as e:
        logger.error(e.__str__())
        logger.error(traceback.print_exc())
        job.update_job(e.__str__(), 'Error')
        send_notification("Probe " + str(probe.name), e.__str__())
        return {"message": "Error for probe " + str(probe.name) + " to deploy rules", "exception": e.__str__()}
    send_notification("Probe " + str(probe.name), "deployed rules successfully")
    return message


@task
def reload_probe(probe_name):
    job = Job.create_job('reload_probe', probe_name)
    probe = Probe.get_by_name(probe_name)
    if probe is None:
        return {"message": "Error - probe is None - param id not set : " + str(probe_name)}
    my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.type)
    probe = my_class.get_by_name(probe_name)
    if probe.scheduled_enabled:
        try:
            message = probe.reload()
            job.update_job(message, 'Completed')
            logger.info("task - reload_probe : " + str(probe_name) + " - " + str(message))
        except Exception as e:
            logger.error(e.__str__())
            logger.error(traceback.print_exc())
            job.update_job(e.__str__(), 'Error')
            send_notification("Probe " + str(probe.name), e.__str__())
            return {"message": "Error for probe " + str(probe.name) + " to reload", "exception": e.__str__()}
        send_notification("Probe " + str(probe.name), "reloaded probe successfully")
        return message
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
    send_notification("Source " + str(source.uri), "Uploaded rules by HTTP successfully")
    return {"message": "OK source " + str(source.uri) + " upload by HTTP", "upload_message": message}
