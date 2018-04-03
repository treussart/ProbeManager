""" venv/bin/python probemanager/manage.py test core.tests.test_views --settings=probemanager.settings.dev """
from django.contrib.auth.models import User
from django.test import Client, TestCase

from core.models import Server, SshKey, OsSupported


class ViewsCoreTest(TestCase):
    fixtures = ['init', 'crontab', 'test-rules-source', 'test-core-secrets']

    def setUp(self):
        self.client = Client()
        User.objects.create_superuser(username='testuser', password='12345', email='testuser@test.com')
        if not self.client.login(username='testuser', password='12345'):
            self.assertRaises(Exception("Not logged"))

    def tearDown(self):
        self.client.logout()

    def test_login(self):
        """
        Django Admin login
        """
        response = self.client.get('/admin/login/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('<title>Site administration | Probe Manager site admin</title>', str(response.content))
        self.assertEqual('admin/index.html', response.templates[0].name)
        self.assertIn('admin', response.resolver_match.app_names)
        self.assertIn('function AdminSite.index', str(response.resolver_match.func))

        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('<a href="/admin/auth/user/" class="changelink">Change</a>', str(response.content))
        self.assertEqual(str(response.context['user']), 'testuser')
        with self.assertTemplateUsed('admin/index.html'):
            self.client.get('/admin/login/', follow=True)

        client_not_logged = Client()
        response = client_not_logged.get('/admin/login/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('<title>Log in | Probe Manager site admin</title>', str(response.content))

        response = client_not_logged.get('/admin/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('<title>Log in | Probe Manager site admin</title>', str(response.content))
        self.assertEqual(str(response.context['user']), 'AnonymousUser')
        response = client_not_logged.get('/admin/')
        self.assertRedirects(response, expected_url='/admin/login/?next=/admin/', status_code=302,
                             target_status_code=200)
        with self.assertTemplateUsed('admin/login.html'):
            client_not_logged.get('/admin/', follow=True)

    def test_index(self):
        """
        Home page
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('<title>Home</title>', str(response.content))
        self.assertEqual('core/index.html', response.templates[0].name)
        self.assertIn('core', response.resolver_match.app_names)
        self.assertIn('function index', str(response.resolver_match.func))
        self.assertEqual(str(response.context['user']), 'testuser')
        with self.assertTemplateUsed('core/index.html'):
            self.client.get('/')

    def test_admin(self):
        response = self.client.get('/admin/core/server/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Server.get_all()), 1)
        response = self.client.post('/admin/core/server/add/', {'name': 'test-server',
                                                                'host': 'test.com',
                                                                'os': '1',
                                                                'remote_user': 'test',
                                                                'remote_port': 22,
                                                                'become_method': 'sudo',
                                                                'become_user': 'root',
                                                                'become_pass': 'test',
                                                                'become': True,
                                                                'ssh_private_key_file': '1',
                                                                },
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(' was added successfully', str(response.content))
        self.assertIn('Connection to the server Failed', str(response.content))
        self.assertEqual(len(Server.get_all()), 2)
