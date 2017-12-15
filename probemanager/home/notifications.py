from pushbullet import Pushbullet
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from home.models import Configuration
import logging

logger = logging.getLogger(__name__)


def send_notification(title, body):
    if Configuration.get_value("PUSHBULLET_API_KEY"):
        pb = Pushbullet(Configuration.get_value("PUSHBULLET_API_KEY"))
        push = pb.push_note(title, body)
        logger.debug(push)


@receiver(post_save, sender=User)
def my_handler(sender, instance, **kwargs):
    send_notification(sender.__name__ + " created", str(instance.username) + " - " + str(instance.email))
