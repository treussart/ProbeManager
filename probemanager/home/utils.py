from django_celery_beat.models import PeriodicTask
import json
import logging
from django.conf import settings
from cryptography.fernet import Fernet
import os
from probemanager.settings import BASE_DIR
from pushbullet import Pushbullet
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


fernet_key = Fernet(settings.FERNET_KEY)
logger = logging.getLogger(__name__)


def create_upload_task(source):
    PeriodicTask.objects.create(crontab=source.scheduled_crontab,
                                name=str(source.uri) + "_upload_task",
                                task='home.tasks.upload_url_http',
                                args=json.dumps([source.uri, ])
                                )


def create_reload_task(probe):
    try:
        PeriodicTask.objects.get(name=probe.name + "_reload_task")
    except PeriodicTask.DoesNotExist:
        PeriodicTask.objects.create(crontab=probe.scheduled_crontab,
                                    name=probe.name + "_reload_task",
                                    task='home.tasks.reload_probe',
                                    args=json.dumps([probe.name, ]))


def create_deploy_rules(probe, schedule=None):
    try:
        if schedule is None:
            try:
                PeriodicTask.objects.get(name=probe.name + "_deploy_rules_" + probe.scheduled_crontab.__str__())
            except PeriodicTask.DoesNotExist:
                PeriodicTask.objects.create(crontab=probe.scheduled_crontab,
                                            name=probe.name + "_deploy_rules_" + probe.scheduled_crontab.__str__(),
                                            task='home.tasks.deploy_rules',
                                            args=json.dumps([probe.name, ]))

        else:
            PeriodicTask.objects.create(crontab=schedule,
                                        name=probe.name + "_source_deploy_rules_" + schedule.__str__(),
                                        task='home.tasks.deploy_rules',
                                        args=json.dumps([probe.name, ]))
    except Exception as e:
        # Error if 2 sources have the same crontab on the same probe -> useless
        logger.debug(e.__str__())


def decrypt(cipher_text):
    if isinstance(cipher_text, bytes):
        return fernet_key.decrypt(cipher_text).decode('utf-8')
    else:
        return fernet_key.decrypt(bytes(cipher_text, 'utf-8'))


def encrypt(plain_text):
    return fernet_key.encrypt(plain_text.encode('utf-8'))


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


def update_progress(value):
    tmpdir = BASE_DIR + "/tmp/"
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)
    if value >= 100:
        os.remove(tmpdir + 'progress.json')
    else:
        progress = dict()
        progress['progress'] = value
        f = open(tmpdir + 'progress.json', 'w')
        f.write(json.dumps(progress))
        f.close()


def send_notification(title, body):
    if settings.PUSHBULLET_API_KEY:
        pb = Pushbullet(settings.PUSHBULLET_API_KEY)
        push = pb.push_note(title, body)
        logger.debug(push)


@receiver(post_save, sender=User)
def my_handler(sender, instance, **kwargs):
    send_notification(sender.__name__ + " created", str(instance.username) + " - " + str(instance.email))
