""" venv/bin/python probemanager/manage.py test core.tests.test_api --settings=probemanager.settings.dev """
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from core.models import Configuration, Server


class APITest(APITestCase):
    fixtures = ['init', 'crontab', 'test-core-secrets']

    def setUp(self):
        self.client = APIClient()
        User.objects.create_superuser(username='testuser', password='12345', email='testuser@test.com')
        if not self.client.login(username='testuser', password='12345'):
            self.assertRaises(Exception("Not logged"))

    def tearDown(self):
        self.client.logout()

    def test_server(self):
        response = self.client.get('/api/v1/core/server/1/test_connection/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'status': True})
        server = Server.get_by_id(1)
        server.become = False
        server.save()
        response = self.client.get('/api/v1/core/server/1/test_connection/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'status': True})

    def test_configuration(self):
        response = self.client.get('/api/v1/core/configuration/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 6)

        data_put = {'value': 'test'}
        data_patch = {'value': 'test'}
        data_patch_2 = {'key': 'test'}

        self.assertEqual(Configuration.objects.get(key="SPLUNK_USER").value, "")

        response = self.client.put('/api/v1/core/configuration/' + str(Configuration.objects.get(key="SPLUNK_USER").id)
                                   + '/', data_put)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(Configuration.objects.get(key="SPLUNK_USER").value, "")

        response = self.client.patch('/api/v1/core/configuration/' +
                                     str(Configuration.objects.get(key="SPLUNK_USER").id) + '/', data_patch)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Configuration.objects.get(key="SPLUNK_USER").value, "test")

        response = self.client.patch('/api/v1/core/configuration/' +
                                     str(Configuration.objects.get(key="SPLUNK_USER").id) + '/', data_patch_2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Configuration.objects.get(key="SPLUNK_USER").key, "SPLUNK_USER")

        response = self.client.get('/api/v1/core/configuration/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 6)

    def test_sshkey(self):
        response = self.client.get('/api/v1/core/sshkey/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

        data = {"name": "test.com_rsa", "file": """-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----"""}

        response = self.client.post('/api/v1/core/sshkey/', data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get('/api/v1/core/sshkey/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
