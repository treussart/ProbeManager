import json
import logging
import os
import time
import shutil
from contextlib import contextmanager

from cryptography.fernet import Fernet
from django.conf import settings
from django_celery_beat.models import PeriodicTask, CrontabSchedule


fernet_key = Fernet(settings.FERNET_KEY)
logger = logging.getLogger(__name__)


def create_reload_task(probe):
    try:
        PeriodicTask.objects.get(name=probe.name + "_reload_task")
    except PeriodicTask.DoesNotExist:
        PeriodicTask.objects.create(crontab=probe.scheduled_rules_deployment_crontab,
                                    name=probe.name + "_reload_task",
                                    task='core.tasks.reload_probe',
                                    args=json.dumps([probe.name, ]))


def create_check_task(probe):
    try:
        PeriodicTask.objects.get(name=probe.name + "_check_task")
    except PeriodicTask.DoesNotExist:
        if probe.scheduled_check_crontab:
            PeriodicTask.objects.create(crontab=probe.scheduled_check_crontab,
                                        name=probe.name + "_check_task",
                                        task='core.tasks.check_probe',
                                        enabled=probe.scheduled_check_enabled,
                                        args=json.dumps([probe.name, ]))
        else:
            PeriodicTask.objects.create(crontab=CrontabSchedule.objects.get(id=4),
                                        name=probe.name + "_check_task",
                                        task='core.tasks.check_probe',
                                        enabled=probe.scheduled_check_enabled,
                                        args=json.dumps([probe.name, ]))


def create_deploy_rules_task(probe, schedule=None, source=None):
    try:
        if schedule is None:
            try:
                PeriodicTask.objects.get(
                    name=probe.name + "_deploy_rules_" + str(probe.scheduled_rules_deployment_crontab))
            except PeriodicTask.DoesNotExist:
                if probe.scheduled_rules_deployment_crontab:
                    PeriodicTask.objects.create(crontab=probe.scheduled_rules_deployment_crontab,
                                                name=probe.name + "_deploy_rules_" + str(
                                                    probe.scheduled_rules_deployment_crontab),
                                                task='core.tasks.deploy_rules',
                                                enabled=probe.scheduled_rules_deployment_enabled,
                                                args=json.dumps([probe.name, ]))
                else:
                    PeriodicTask.objects.create(crontab=CrontabSchedule.objects.get(id=4),
                                                name=probe.name + "_deploy_rules_" + str(
                                                    probe.scheduled_rules_deployment_crontab),
                                                task='core.tasks.deploy_rules',
                                                enabled=probe.scheduled_rules_deployment_enabled,
                                                args=json.dumps([probe.name, ]))
        elif source is not None:
            try:
                PeriodicTask.objects.get(name=probe.name + "_" + source.uri + "_deploy_rules_" + str(schedule))
            except PeriodicTask.DoesNotExist:
                PeriodicTask.objects.create(crontab=schedule,
                                            name=probe.name + "_" + source.uri + "_deploy_rules_" + str(schedule),
                                            task='core.tasks.deploy_rules',
                                            enabled=probe.scheduled_rules_deployment_enabled,
                                            args=json.dumps([probe.name, ]))
    except Exception:
        logger.warning("Error if 2 sources have the same crontab on the same probe -> useless")


def decrypt(cipher_text):
    if isinstance(cipher_text, bytes):
        return fernet_key.decrypt(cipher_text)
    else:
        return fernet_key.decrypt(cipher_text.encode('utf-8')).decode('utf-8')


def encrypt(plain_text):
    if isinstance(plain_text, bytes):
        return fernet_key.encrypt(plain_text)
    else:
        return fernet_key.encrypt(plain_text.encode('utf-8')).decode('utf-8')


def add_10_min(crontab):
    schedule = crontab
    try:
        if schedule.minute == '*':
            # print("* -> 10")
            schedule.minute = '10'
            return schedule
        elif schedule.minute.isdigit():
            if int(schedule.minute) in range(0, 49):
                # print("0-50 -> +10")
                minute = int(schedule.minute)
                minute += 10
                schedule.minute = str(minute)
                return schedule
            elif schedule.hour.isdigit():
                hour = schedule.hour
                if int(hour) in range(0, 22):
                    # print("50+ H0-22 -> H + 1 - 50")
                    hour = int(schedule.hour)
                    hour += 1
                    schedule.hour = str(hour)
                    minute = int(schedule.minute)
                    schedule.minute = str(minute - 50)
                    return schedule
                else:
                    # print("50+ H23 -> ?")
                    return schedule
            elif schedule.hour == '*':
                # print("50+ H* -> -50 +1H")
                minute = int(schedule.minute)
                schedule.minute = str(minute - 50)
                schedule.hour = '*/1'
                return schedule
            else:
                hour = int(schedule.hour[2:])
                # print("50+ H*/0+ -> +1h -50min")
                schedule.hour = '*/' + str(hour + 1)
                schedule.minute = str(int(schedule.minute) - 50)
                return schedule
        elif '/' in schedule.minute and int(schedule.minute[2:]) in range(10, 49):
            # print("*/0-49 -> +10min")
            minute = int(schedule.minute[2:])
            minute += 10
            schedule.minute = '*/' + str(minute)
            return schedule
        elif '/' in schedule.minute and int(schedule.minute[2:]) not in range(10, 49):
            if schedule.hour.isdigit():
                hour = int(schedule.hour)
                if hour in range(0, 22):
                    # print("*/50+  H0-22 -> +1H -50min")
                    hour += 1
                    schedule.hour = str(hour)
                    schedule.minute = '10'
                    return schedule
                else:
                    # print("*/50+  H23 -> ?")
                    return schedule
        else:  # pragma: no cover
            raise ValueError()
    except ValueError:
        return schedule


def add_1_hour(crontab):
    schedule = crontab
    try:
        if schedule.minute.isdigit():
            if schedule.hour.isdigit():
                hour = schedule.hour
                if int(hour) in range(0, 22):
                    # 2 1  ->  2 2
                    hour = int(schedule.hour)
                    hour += 1
                    schedule.hour = str(hour)
                    return schedule
                else:
                    # 2 23 -> 2 0  + 1 jour
                    if schedule.day_of_week.isdigit():
                        schedule.hour = str(0)
                        if int(schedule.day_of_week) in range(0, 5):
                            schedule.day_of_week = str(int(schedule.day_of_week) + 1)
                        else:
                            schedule.day_of_week = str(0)
                    else:
                        # 2 23 * -> 2 0  + 1 jour illogic
                        pass
                    return schedule
            else:
                # 50 * -> equal  illogic
                # 10 */2 -> equal  illogic
                return schedule
        else:
            # */2 1 ->  */2 2 illogic
            # */2 * ->  equal  illogic
            # * 23 -> * 0  + 1 jour  illogic
            # * 1 -> * 2  illogic
            return schedule
    except ValueError:
        return schedule


@contextmanager
def get_tmp_dir(folder_name=None):
    if folder_name:
        tmp_dir = settings.BASE_DIR + '/tmp/' + str(folder_name) + '/' + str(time.time()) + '/'
    else:
        tmp_dir = settings.BASE_DIR + '/tmp/' + str(time.time()) + '/'
    try:
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        yield tmp_dir
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
