""" venv/bin/python probemanager/manage.py test core.tests.test_tasks --settings=probemanager.settings.dev """
from django.conf import settings
from django.test import TestCase

from core.tasks import deploy_rules, reload_probe, install_probe, update_probe, check_probe


class TasksCoreTest(TestCase):
    fixtures = ['init', 'crontab', 'test-rules-source', 'test-core-secrets', 'test-core-probe']

    @classmethod
    def setUpTestData(cls):
        settings.CELERY_TASK_ALWAYS_EAGER = True

    def test_deploy_rules(self):
        response = deploy_rules.delay('bad')
        self.assertEqual(response.get(), {"message": "Error - probe is None - param id not set : " + 'bad'})
        self.assertTrue(response.successful())

    def test_reload_probe(self):
        response = reload_probe.delay('bad')
        self.assertEqual(response.get(), {"message": "Error - probe is None - param id not set : " + 'bad'})
        self.assertTrue(response.successful())

    def test_install_probe(self):
        response = install_probe.delay('bad')
        self.assertEqual(response.get(), {"message": "Error - probe is None - param id not set : " + 'bad'})
        self.assertTrue(response.successful())

    def test_update_probe(self):
        response = update_probe.delay('bad')
        self.assertEqual(response.get(), {"message": "Error - probe is None - param id not set : " + 'bad'})
        self.assertTrue(response.successful())

    def test_check_probe(self):
        response = check_probe.delay('bad')
        self.assertEqual(response.get(), {"message": "Error - probe is None - param id not set : " + 'bad'})
        self.assertTrue(response.successful())
