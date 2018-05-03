""" venv/bin/python probemanager/manage.py test core.tests.test_ssh --settings=probemanager.settings.dev """
from django.conf import settings
from django.test import TestCase

from core.models import Server
from core.ssh import connection, execute, execute_copy


class SshCoreTest(TestCase):
    fixtures = ['init', 'test-core-secrets']

    @classmethod
    def setUpTestData(cls):
        pass

    def test_connection(self):
        server = Server.get_by_id(1)
        client = connection(server)
        stdin, stdout, stderr = client.exec_command("hostname")
        self.assertEqual(stdout.channel.recv_exit_status(), 0)
        self.assertEqual(stdout.read().decode('utf-8'), 'test-travis\n')
        self.assertEqual(stderr.readlines(), [])
        client.close()

    def test_execute(self):
        server = Server.get_by_id(1)
        self.assertEqual(execute(server, {'test_hostame': "hostname"}, become=False),
                         {'test_hostame': 'test-travis'})
        self.assertEqual(execute(server, {'test_ok': "hostname 1>/dev/null"}, become=False),
                         {'test_ok': 'OK'})
        with self.assertRaises(Exception):
            execute(server, {'test_fail': "service ssh status"}, become=False)

    def test_execute_become(self):
        server = Server.get_by_id(1)
        self.assertEqual(execute(server, {'test_hostame': "hostname"}, become=True),
                         {'test_hostame': 'test-travis'})
        self.assertIn('ssh.service', execute(server, {'test_status': "service ssh status"}, become=True)['test_status'])
        server.become_pass = None
        server.save()
        with self.assertRaises(Exception):
            self.assertEqual(execute(server, {'test_hostame': "hostname"}, become=True),
                             {'test_hostame': 'test-travis'})

        server.become = False
        server.save()
        with self.assertRaises(Exception):
            self.assertEqual(execute(server, {'test_hostame': "hostname"}, become=True),
                             {'test_hostame': 'test-travis'})

    def test_execute_copy_put(self):
        server = Server.get_by_id(1)
        result = execute_copy(server, src=settings.ROOT_DIR + '/LICENSE', dest='LICENSE')
        self.assertEqual(result, {'copy': 'OK'})

    def test_execute_copy_put_become(self):
        server = Server.get_by_id(1)
        result = execute_copy(server, src=settings.ROOT_DIR + '/LICENSE', dest='/tmp/LICENSE', become=True)
        self.assertEqual(result, {'copy': 'OK', 'mv': {'mv': 'OK'}})
