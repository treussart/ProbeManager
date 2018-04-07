""" venv/bin/python probemanager/manage.py test core.tests.test_models --settings=probemanager.settings.dev """
import pytz

from django.db.utils import IntegrityError
from django.test import TestCase
from datetime import timedelta, datetime
from core.models import OsSupported, Probe, ProbeConfiguration, SshKey, Job, Server, Configuration


class JobTest(TestCase):
    fixtures = ['init']

    @classmethod
    def setUpTestData(cls):
        now = datetime(year=2017, month=5, day=5, hour=12, tzinfo=pytz.UTC)
        before = now - timedelta(minutes=30)
        cls.job1 = Job.objects.create(name="test", probe="test", status='Error', result="",
                                      created=before, completed=now)
        cls.job2 = Job.create_job('test2', 'probe1')

    def test_job(self):
        self.assertEqual(str(self.job1), 'test')
        self.assertEqual(str(self.job1.get_duration()), '-1 day, 23:30:00')
        self.assertEqual(str(self.job2), 'test2')
        self.assertEqual(self.job2.status, 'In progress')
        self.job2.update_job('test model', 'Completed')
        self.assertEqual(self.job2.status, 'Completed')
        jobs = Job.get_all()
        self.assertTrue(jobs[0].created > jobs[1].created)


class OsSupportedTest(TestCase):
    fixtures = ['init']
    multi_db = False

    @classmethod
    def setUpTestData(cls):
        pass

    def test_os_supported(self):
        all_os_supported = OsSupported.get_all()
        os_supported = OsSupported.get_by_id(1)
        self.assertEqual(len(all_os_supported), 2)
        self.assertEqual(os_supported.name, "debian")
        self.assertEqual(str(os_supported), "debian")
        # Mixins
        self.assertEqual(OsSupported.get_last(), OsSupported.get_by_id(2))
        self.assertEqual(OsSupported.get_nbr(1)[0], os_supported)
        OsSupported.get_by_id(1).delete()
        OsSupported.get_by_id(2).delete()
        self.assertEqual(OsSupported.get_last(), None)
        os_supported = OsSupported.get_by_id(99)
        self.assertEqual(os_supported, None)
        with self.assertRaises(AttributeError):
            os_supported.name
        with self.assertLogs('core.models', level='DEBUG'):
            OsSupported.get_by_id(99)
        OsSupported.objects.create(name='debian')
        with self.assertRaises(IntegrityError):
            OsSupported.objects.create(name="debian")


class ProbeConfigurationTest(TestCase):
    fixtures = ['init', 'test-core-probeconfiguration']

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
        with self.assertLogs('core.models', level='DEBUG'):
            ProbeConfiguration.get_by_id(99)
        with self.assertRaises(IntegrityError):
            ProbeConfiguration.objects.create(name="conf1")


class SshKeyTest(TestCase):
    fixtures = ['init', 'crontab', 'test-core-sshkey']

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
    fixtures = ['init', 'crontab', 'test-core-server', 'test-core-probe']

    @classmethod
    def setUpTestData(cls):
        pass

    def test_probe(self):
        all_probe = Probe.get_all()
        probe = Probe.get_by_id(1)
        self.assertEqual(Probe.get_by_name("probe1"), Probe.get_by_id(1))
        self.assertEqual(len(all_probe), 1)
        self.assertEqual(probe.name, "probe1")
        self.assertEqual(str(probe), "probe1")
        self.assertEqual(probe.description, "test")
        self.assertIn('Failed to get the uptime on the host :', probe.uptime())
        self.assertFalse(probe.start()['status'])
        self.assertFalse(probe.restart()['status'])
        self.assertFalse(probe.stop()['status'])
        self.assertFalse(probe.reload()['status'])
        self.assertEqual('Failed to get status', probe.status())
        probe.installed = False
        self.assertEqual('Not installed', probe.uptime())
        probe = Probe.get_by_id(99)
        self.assertEqual(probe, None)
        with self.assertRaises(AttributeError):
            probe.name
        probe = Probe.get_by_name("probe99")
        self.assertEqual(probe, None)
        with self.assertRaises(AttributeError):
            probe.name
        with self.assertLogs('core.models', level='DEBUG'):
            Probe.get_by_id(99)
        with self.assertLogs('core.models', level='DEBUG'):
            Probe.get_by_name('probe99')
        with self.assertRaises(IntegrityError):
            Probe.objects.create(name="suricata1")


class ServerTest(TestCase):
    fixtures = ['init', 'crontab', 'test-core-server', 'test-core-probe']

    @classmethod
    def setUpTestData(cls):
        pass

    def test_server(self):
        self.assertEqual(Server.get_by_host("localhost"), Server.get_by_id(1))
        self.assertFalse(Server.get_by_host("localhost").test())
        self.assertFalse(Server.get_by_host("localhost").test_root())
        self.assertEqual(Server.get_by_host("unknown"), None)


class ConfTest(TestCase):
    fixtures = ['init', 'crontab', 'test-core-probeconfiguration', 'test-core-server', 'test-core-probe']

    @classmethod
    def setUpTestData(cls):
        pass

    def test_conf(self):
        conf = Configuration.objects.get(id=1)
        self.assertEqual(str(conf), "PUSHBULLET_API_KEY")
        self.assertEqual(conf.get_value('inexist'), None)
