""" python manage.py test home.tests.test_models --settings=probemanager.settings.dev """
from django.test import TestCase
from home.models import OsSupported, Probe, ProbeConfiguration, SshKey
from django.db.utils import IntegrityError
# from unittest import skip


class OsSupportedTest(TestCase):
    fixtures = ['init']
    multi_db = False

    @classmethod
    def setUpTestData(cls):
        pass

    def test_os_supported(self):
        all_os_supported = OsSupported.get_all()
        os_supported = OsSupported.get_by_id(1)
        self.assertEqual(len(all_os_supported), 1)
        self.assertEqual(os_supported.name, "debian")
        self.assertEqual(str(os_supported), "debian")
        os_supported = OsSupported.get_by_id(99)
        self.assertEqual(os_supported, None)
        with self.assertRaises(AttributeError):
            os_supported.name
        with self.assertLogs('home.models', level='DEBUG'):
            OsSupported.get_by_id(99)
        with self.assertRaises(IntegrityError):
            OsSupported.objects.create(name="debian")


class ProbeConfigurationTest(TestCase):
    fixtures = ['init', 'test-home-probeconfiguration']

    @classmethod
    def setUpTestData(cls):
        pass

    def test_probe_configuration(self):
        all_probe_configuration = ProbeConfiguration.get_all()
        probe_configuration = ProbeConfiguration.get_by_id(1)
        self.assertEqual(len(all_probe_configuration), 1)
        self.assertEqual(probe_configuration.name, "conf1")
        self.assertEqual(str(probe_configuration), "conf1")
        probe_configuration = ProbeConfiguration.get_by_id(99)
        self.assertEqual(probe_configuration, None)
        with self.assertRaises(AttributeError):
            probe_configuration.name
        with self.assertLogs('home.models', level='DEBUG'):
            ProbeConfiguration.get_by_id(99)
        with self.assertRaises(IntegrityError):
            ProbeConfiguration.objects.create(name="conf1")


class SshKeyTest(TestCase):
    fixtures = ['init', 'crontab', 'test-home-sshkey']

    @classmethod
    def setUpTestData(cls):
        pass

    def test_sshKey(self):
        ssh_key = SshKey.objects.get(id=1)
        self.assertEqual(ssh_key.name, 'test')
        self.assertEqual(str(ssh_key), "test")
        with self.assertRaises(SshKey.DoesNotExist):
            SshKey.objects.get(id=199)
        with self.assertRaises(IntegrityError):
            SshKey.objects.create(name="test")


class ProbeTest(TestCase):
    fixtures = ['init', 'crontab', 'test-suricata-script', 'test-suricata-signature', 'test-suricata-ruleset', 'test-suricata-conf', 'test-suricata-probe']

    @classmethod
    def setUpTestData(cls):
        pass

    def test_probe(self):
        all_probe = Probe.get_all()
        probe = Probe.get_by_id(1)
        self.assertEqual(Probe.get_by_name("suricata1"), Probe.get_by_id(1))
        self.assertEqual(len(all_probe), 2)
        self.assertEqual(probe.name, "suricata1")
        self.assertEqual(str(probe), "suricata1")
        self.assertEqual(probe.description, "test")
        response = probe.test()
        self.assertEqual(0, response['result'])
        response = probe.test_root()
        print(response)
        self.assertEqual(0, response['result'])
        response = probe.status()
        self.assertEqual(2, response['result'])
        self.assertEqual('Unit probe.service could not be found.', response['message']['stderr'])
        response = probe.reload()
        self.assertEqual(2, response['result'])
        self.assertEqual('probe: unrecognized service', response['message']['stderr'])
        response = probe.stop()
        self.assertEqual(2, response['result'])
        self.assertEqual('Could not find the requested service probe: host', response['message']['msg'])
        response = probe.start()
        self.assertEqual(2, response['result'])
        self.assertEqual('Could not find the requested service probe: host', response['message']['msg'])
        response = probe.restart()
        self.assertEqual(2, response['result'])
        self.assertEqual('Could not find the requested service probe: host', response['message']['msg'])
        response = probe.install()
        self.assertEqual(2, response['result'])
        response = probe.update()
        self.assertEqual(2, response['result'])

        probe = Probe.get_by_id(99)
        self.assertEqual(probe, None)
        with self.assertRaises(AttributeError):
            probe.name
        probe = Probe.get_by_name("probe99")
        self.assertEqual(probe, None)
        with self.assertRaises(AttributeError):
            probe.name
        with self.assertLogs('home.models', level='DEBUG'):
            Probe.get_by_id(99)
        with self.assertLogs('home.models', level='DEBUG'):
            Probe.get_by_name('probe99')
        with self.assertRaises(IntegrityError):
            Probe.objects.create(name="suricata1")
