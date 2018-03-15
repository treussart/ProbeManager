""" venv/bin/python probemanager/manage.py test core.tests.test_notifications --settings=probemanager.settings.dev """
import configparser
import os

from django.test import TestCase
from django.conf import settings
from pushbullet.errors import InvalidKeyError

from core.models import Configuration
from core.notifications import send_notification


class NotificationsTest(TestCase):
    fixtures = ['init', 'test-core-secrets']

    @classmethod
    def setUpTestData(cls):
        config = configparser.ConfigParser()
        config.read(os.path.join(settings.BASE_DIR, 'core/fixtures/test-core-secrets.ini'))
        settings.configure(DEBUG=True)

    def test_push_empty(self):
        send_notification("test", "test")

    def test_push_ok(self):
        send_notification("test", "test")

    def test_push_fail(self):
        api = Configuration.objects.get(key="PUSHBULLET_API_KEY")
        api.value = "o.nkN6cvwybstW58"
        api.save()
        with self.assertRaises(InvalidKeyError):
            send_notification("test", "test")

    def test_email(self):
        pass
