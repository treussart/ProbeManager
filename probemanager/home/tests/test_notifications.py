""" python probemanager/manage.py test home.tests.test_notifications """
from django.test import TestCase
from home.notifications import send_notification
from home.models import Configuration
from pushbullet.errors import InvalidKeyError


class NotificationsTest(TestCase):
    fixtures = ['init', ]

    @classmethod
    def setUpTestData(cls):
        pass

    def test_push_empty(self):
        send_notification("test", "test")

    def test_push_ok(self):
        api = Configuration.objects.get(key="PUSHBULLET_API_KEY")
        api.value = "o.nkN6cvwybstW58883xfDOjAZPf3Z3zl4"
        api.save()
        send_notification("test", "test")

    def test_push_fail(self):
        api = Configuration.objects.get(key="PUSHBULLET_API_KEY")
        api.value = "o.nkN6cvwybstW58"
        api.save()
        with self.assertRaises(InvalidKeyError):
            send_notification("test", "test")
