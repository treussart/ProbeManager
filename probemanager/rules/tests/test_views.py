""" python manage.py test rules.tests.test_views """
from django.test import Client, TestCase
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.utils import timezone
# from unittest import skip


class ViewsRulesTest(TestCase):
    fixtures = ['init', 'crontab', 'test-suricata-signature', 'test-suricata-script']

    def setUp(self):
        self.client = Client()
        User.objects.create_superuser(username='testuser', password='12345', email='testuser@test.com')
        if not self.client.login(username='testuser', password='12345'):
            self.assertRaises(Exception("Not logged"))
        self.date_now = timezone.now()

    def tearDown(self):
        pass
        # self.client.logout()

    def test_search(self):
        """
        Search page
        """
        response = self.client.get(reverse('rules:search'), {'pattern': 'DNS'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('<title>Result Rules</title>', str(response.content))
        self.assertEqual('rules/search.html', response.templates[0].name)
        self.assertIn('rules', response.resolver_match.app_names)
        self.assertIn('function search', str(response.resolver_match.func))
        self.assertEqual(str(response.context['user']), 'testuser')
        with self.assertTemplateUsed('rules/search.html'):
            self.client.get(reverse('rules:search'), {'pattern': 'DNS'})
        response = self.client.get(reverse('rules:search'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Pattern not found', str(response.content))
        response = self.client.get(reverse('rules:search'), {'pattern': ''})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Pattern not found', str(response.content))
        response = self.client.get(reverse('rules:search'), {'pattern': ' '})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Pattern   not found', str(response.content))
        response = self.client.get(reverse('rules:search'), {'pattern': '-oywz'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Result Rules', str(response.content))
