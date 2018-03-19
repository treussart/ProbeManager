""" venv/bin/python probemanager/manage.py test core.tests.test_notifications --settings=probemanager.settings.dev """
import configparser
import os

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User

from core.models import Configuration
from core.notifications import send_notification


class NotificationsCoreTest(TestCase):
    fixtures = ['init', 'test-core-secrets']

    @classmethod
    def setUpTestData(cls):
        config = configparser.ConfigParser()
        config.read(os.path.join(settings.BASE_DIR, 'core/fixtures/test-core-secrets.ini'))
        settings.EMAIL_HOST=config['EMAIL']['EMAIL_HOST']
        settings.EMAIL_PORT=int(config['EMAIL']['EMAIL_PORT'])
        settings.EMAIL_HOST_USER=config['EMAIL']['EMAIL_HOST_USER']
        settings.DEFAULT_FROM_EMAIL=config['EMAIL']['DEFAULT_FROM_EMAIL']
        settings.EMAIL_USE_TLS=config.getboolean('EMAIL', 'EMAIL_USE_TLS')
        settings.EMAIL_HOST_PASSWORD=config['EMAIL']['EMAIL_HOST_PASSWORD']
        User.objects.create_superuser(username='usertest', password='12345', email='matthieu@treussart.com')

    def test_push_fail(self):
        api = Configuration.objects.get(key="PUSHBULLET_API_KEY")
        api.value = "o.nkN6cvwybstW58"
        api.save()
        with self.assertLogs('core.notifications', level='ERROR'):
            send_notification("test", "test")
