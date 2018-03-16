""" venv/bin/python probemanager/manage.py test core.tests.test_ssh --settings=probemanager.settings.dev """
from django.test import TestCase


from django.conf import settings
from core.ssh import connection, execute, execute_copy
from core.models import Server


class SshTest(TestCase):
    fixtures = ['init', 'test-core-secrets']

    @classmethod
    def setUpTestData(cls):
        pass

    def test_connection(self):
        server = Server.get_by_id(1)
        client = connection(server)
        stdin, stdout, stderr = client.exec_command("hostname")
        self.assertEqual(stdout.channel.recv_exit_status(), 0)
        self.assertEqual(stdout.read().decode('utf-8'), 'server\n')
        self.assertEqual(stderr.readlines(), [])
        client.close()

    def test_execute(self):
        server = Server.get_by_id(1)
        result = execute(server, {'test_hostame': "hostname"}, become=False)
        self.assertEqual(result, {'test_hostame': 'server'})

    def test_execute_become(self):
        server = Server.get_by_id(1)
        result = execute(server, {'test_hostame': "hostname"}, become=True)
        self.assertEqual(result, {'test_hostame': 'server'})

    def test_execute_copy_put(self):
        server = Server.get_by_id(1)
        result = execute_copy(server, src=settings.ROOT_DIR + '/LICENSE', dest='LICENSE')
        self.assertEqual(result, {'copy': 'OK'})

    def test_execute_copy_put_become(self):
        server = Server.get_by_id(1)
        result = execute_copy(server, src=settings.ROOT_DIR + '/LICENSE', dest='/tmp/LICENSE', become=True)
        self.assertEqual(result, {'copy': 'OK', 'mv': {'mv': 'OK'}})
