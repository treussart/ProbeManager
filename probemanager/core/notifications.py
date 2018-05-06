import logging
from smtplib import SMTPException

import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from lxml import html as html_lxml
from pushbullet import Pushbullet
from pushbullet.errors import InvalidKeyError, PushError

from .models import Configuration

logger = logging.getLogger('core.notifications')


def pushbullet(title, plain_body):  # pragma: no cover
    if Configuration.get_value("PUSHBULLET_API_KEY"):
        try:
            pb = Pushbullet(Configuration.get_value("PUSHBULLET_API_KEY"))
            push = pb.push_note(title, plain_body)
            logger.debug(push)
        except InvalidKeyError:
            logger.exception('Wrong PUSHBULLET_API_KEY')
        except PushError:
            logger.exception('Pushbullet pro required - too many notifications generated')


def splunk(html_body):  # pragma: no cover
    if Configuration.get_value("SPLUNK_HOST"):
        if Configuration.get_value("SPLUNK_USER") and Configuration.get_value("SPLUNK_PASSWORD"):
            url = "https://" + Configuration.get_value(
                "SPLUNK_HOST") + ":8089/services/receivers/simple?source=ProbeManager&sourcetype=notification"
            r = requests.post(url, verify=False, data=html_body,
                              auth=(Configuration.get_value("SPLUNK_USER"), Configuration.get_value("SPLUNK_PASSWORD")))
        else:
            url = "https://" + Configuration.get_value(
                "SPLUNK_HOST") + ":8089/services/receivers/simple?source=ProbeManager&sourcetype=notification"
            r = requests.post(url, verify=False, data=html_body)
        logger.debug("Splunk " + str(r.text))


def email(title, plain_body, html_body):  # pragma: no cover
    users = User.objects.all()
    if settings.DEFAULT_FROM_EMAIL:
        try:
            for user in users:
                if user.is_superuser:
                    try:
                        user.email_user(title, plain_body, html_message=html_body)
                    except AttributeError:
                        logger.exception("Error in sending email")
        except SMTPException:
            logger.exception("Error in sending email")
        except ConnectionRefusedError:
            logger.exception("Error in sending email")


def send_notification(title, body, html=False):  # pragma: no cover
    if html:
        plain_body = html_lxml.fromstring(body).text_content()
        html_body = body
    else:
        plain_body = body
        html_body = '<pre>' + body + '</pre>'
    # Pushbullet
    pushbullet(title, plain_body)
    # Splunk
    splunk(html_body)
    # Email
    email(title, plain_body, html_body)


@receiver(post_save, sender=User)
def my_handler(sender, instance, **kwargs):  # pragma: no cover
    send_notification(sender.__name__ + " created", str(instance.username) + " - " + str(instance.email))
