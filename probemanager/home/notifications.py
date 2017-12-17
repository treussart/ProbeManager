from pushbullet import Pushbullet
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from home.models import Configuration
from django.conf import settings
import logging
from lxml import html as html_lxml


logger = logging.getLogger(__name__)


def send_notification(title, body, html=False):
    if html:
        plain_body = html_lxml.fromstring(body).text_content()
        html_body = body
    else:
        plain_body = body
        html_body = '<pre>' + body + '</pre>'
    # Push
    if Configuration.get_value("PUSHBULLET_API_KEY"):
        pb = Pushbullet(Configuration.get_value("PUSHBULLET_API_KEY"))
        push = pb.push_note(title, plain_body)
        logger.debug(push)
    # Email
    users = User.objects.all()
    if settings.DEFAULT_FROM_EMAIL:
        try:
            for user in users:
                if user.is_superuser:
                    user.email_user(title, html_message=html_body, from_email=settings.DEFAULT_FROM_EMAI)
        except ConnectionRefusedError:
            pass


@receiver(post_save, sender=User)
def my_handler(sender, instance, **kwargs):
    send_notification(sender.__name__ + " created", str(instance.username) + " - " + str(instance.email))
