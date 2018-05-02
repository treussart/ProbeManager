""" venv/bin/python probemanager/manage.py test core.tests.test_api --settings=probemanager.settings.dev """
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from core.models import Configuration


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

        data = {"name": "test2", "file": "ssh_keys/test.com_rsa"}

        response = self.client.post('/api/v1/core/sshkey/', data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get('/api/v1/core/sshkey/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
