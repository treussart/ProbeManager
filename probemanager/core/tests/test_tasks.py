""" venv/bin/python probemanager/manage.py test core.tests.test_tasks --settings=probemanager.settings.dev """
from django.test import TestCase

from core.models import Probe
from core.tasks import deploy_rules, reload_probe, install_probe, update_probe, check_probe


class TasksRulesTest(TestCase):
    fixtures = ['init', 'crontab', 'test-rules-source', 'test-core-secrets', 'test-core-probe']

    @classmethod
    def setUpTestData(cls):
        pass

    def test_deploy_rules(self):
        with self.assertRaises(TypeError):
            deploy_rules(Probe.get_by_id(1).name)
        self.assertEqual(deploy_rules('bad'), {"message": "Error - probe is None - param id not set : " + 'bad'})
        # self.assertEqual(deploy_rules(None), {"message": "Error - probe is None - param id not set : " + 'None'})

    def test_reload_probe(self):
        with self.assertRaises(TypeError):
            reload_probe(Probe.get_by_id(1).name)
        self.assertEqual(reload_probe('bad'), {"message": "Error - probe is None - param id not set : " + 'bad'})
        # self.assertEqual(reload_probe(None), {"message": "Error - probe is None - param id not set : " + 'None'})

    def test_install_probe(self):
        with self.assertRaises(TypeError):
            install_probe(Probe.get_by_id(1).name)
        self.assertEqual(install_probe('bad'), {"message": "Error - probe is None - param id not set : " + 'bad'})

    def test_update_probe(self):
        with self.assertRaises(TypeError):
            update_probe(Probe.get_by_id(1).name)
        self.assertEqual(update_probe('bad'), {"message": "Error - probe is None - param id not set : " + 'bad'})

    def test_check_probe(self):
        with self.assertRaises(TypeError):
            check_probe(Probe.get_by_id(1).name)
        self.assertEqual(check_probe('bad'), {"message": "Error - probe is None - param id not set : " + 'bad'})
