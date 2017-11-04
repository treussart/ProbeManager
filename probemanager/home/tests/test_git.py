""" python manage.py test home.tests.test_git """
from django.test import TestCase
from home.git import git_tag
from probemanager.settings.base import GIT_ROOT


class GitTest(TestCase):
    fixtures = ['init', 'crontab']

    @classmethod
    def setUpTestData(cls):
        pass

    def test_git_tag(self):
        version = git_tag(GIT_ROOT)
        self.assertIn("v1.0-", version)
