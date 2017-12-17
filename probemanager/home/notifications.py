from pushbullet import Pushbullet
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from home.models import Configuration
from django.conf import settings
import logging
import requests
from lxml import html as html_lxml


logger = logging.getLogger('home')


def send_notification(title, body, html=False):
    if html:
        plain_body = html_lxml.fromstring(body).text_content()
        html_body = body
    else:
        plain_body = body
        html_body = '<pre>' + body + '</pre>'
    # Pushbullet
    if Configuration.get_value("PUSHBULLET_API_KEY"):
        pb = Pushbullet(Configuration.get_value("PUSHBULLET_API_KEY"))
        push = pb.push_note(title, plain_body)
        logger.debug(push)
    # Splunk
    if Configuration.get_value("SPLUNK_HOST"):
        if Configuration.get_value("SPLUNK_USER") and Configuration.get_value("SPLUNK_PASSWORD"):
            # output = subprocess.getoutput(["curl", "-u", Configuration.get_value("SPLUNK_USER") + ":" + Configuration.get_value("SPLUNK_PASSWORD"), "-k", "https://" + Configuration.get_value("SPLUNK_HOST") + ":8089/services/receivers/simple?source=ProbeManager&sourcetype=notification", "-d", body])
            url = "https://" + Configuration.get_value("SPLUNK_HOST") + ":8089/services/receivers/simple?source=ProbeManager&sourcetype=notification"
            files = {'file': ('notification.json', plain_body, {'Expires': '0'})}
            r = requests.post(url, files=files, headers={'Authorization': Configuration.get_value("SPLUNK_USER") + ":" + Configuration.get_value("SPLUNK_PASSWORD")})

        else:
            url = "https://" + Configuration.get_value("SPLUNK_HOST") + ":8089/services/receivers/simple?source=ProbeManager&sourcetype=notification"
            files = {'file': ('notification.json', plain_body, {'Expires': '0'})}
            r = requests.post(url, files=files)
            # output = subprocess.getoutput(["curl", "-k", "https://" + Configuration.get_value("SPLUNK_HOST") + ":8089/services/receivers/simple?source=ProbeManager&sourcetype=notification", "-d", body])
            # output = subprocess.getoutput("curl -d '" + plain_body + "' -H 'Content-Type: application/json' -X POST -k https://" + Configuration.get_value("SPLUNK_HOST") + ":8089/services/receivers/simple?source=ProbeManager&sourcetype=notification")
        logger.debug("Splunk " + str(r.text))
    # Email
    users = User.objects.all()
    if settings.DEFAULT_FROM_EMAIL:
        try:
            for user in users:
                if user.is_superuser:
                    user.email_user(title, plain_body, html_message=html_body, from_email=None)
        except ConnectionRefusedError:
            pass


@receiver(post_save, sender=User)
def my_handler(sender, instance, **kwargs):
    send_notification(sender.__name__ + " created", str(instance.username) + " - " + str(instance.email))
