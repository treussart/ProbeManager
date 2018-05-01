import logging
import time

from django.db import models
from django.utils import timezone
from django_celery_beat.models import CrontabSchedule

from core.modelsmixins import CommonMixin

logger = logging.getLogger(__name__)


class Rule(CommonMixin, models.Model):
    """
    Represent a rule, who can be a script or a signature.
    """
    id = models.AutoField(primary_key=True)
    rev = models.IntegerField(default=0)
    reference = models.CharField(max_length=1000, blank=True, null=True)
    rule_full = models.TextField(max_length=10000)
    enabled = models.BooleanField(default=True)
    created_date = models.DateTimeField(default=timezone.now, editable=False)
    updated_date = models.DateTimeField(default=timezone.now, editable=False)
    file_test_success = models.FileField(name='file_test_success', upload_to='file_test_success', blank=True)

    @classmethod
    def find(cls, pattern):
        """Search the pattern in all the scripts and signatures"""
        return cls.objects.filter(rule_full__icontains=pattern)


class DataTypeUpload(CommonMixin, models.Model):
    """
    Data type, for differentiate the uploaded file (compressed, uncompressed, multiple files, one file).
    """
    name = models.CharField(max_length=100, unique=True, blank=False, null=False)

    def __str__(self):
        return self.name

    @classmethod
    def get_by_name(cls, name):
        try:
            obj = cls.objects.get(name=name)
        except cls.DoesNotExist as e:
            logger.debug('Tries to access an object that does not exist : ' + str(e))
            return None
        return obj


class MethodUpload(CommonMixin, models.Model):
    """
    Method use for the upload. By URL, File
    """
    name = models.CharField(max_length=100, unique=True, blank=False, null=False)

    def __str__(self):
        return self.name

    @classmethod
    def get_by_name(cls, name):
        try:
            obj = cls.objects.get(name=name)
        except cls.DoesNotExist as e:
            logger.debug('Tries to access an object that does not exist : ' + str(e))
            return None
        return obj


class RuleSet(CommonMixin, models.Model):
    """
    Set of Rules. Scripts and signatures.
    """
    name = models.CharField(max_length=100, unique=True, blank=False, null=False, db_index=True,
                            verbose_name="Ruleset name")
    description = models.CharField(max_length=400, blank=True)
    created_date = models.DateTimeField(default=timezone.now, editable=False)
    updated_date = models.DateTimeField(blank=True, null=True, editable=False)

    def __str__(self):
        return self.name

    @classmethod
    def get_by_name(cls, name):
        try:
            obj = cls.objects.get(name=name)
        except cls.DoesNotExist as e:
            logger.debug('Tries to access an object that does not exist : ' + str(e))
            return None
        return obj


class Source(CommonMixin, models.Model):
    """
    Set of Source. For scheduled upload of rules.
    """
    method = models.ForeignKey(MethodUpload, on_delete=models.CASCADE)
    data_type = models.ForeignKey(DataTypeUpload, on_delete=models.CASCADE)
    uri = models.CharField(max_length=1000, unique=True, blank=True, null=False)
    scheduled_rules_deployment_enabled = models.BooleanField(default=False)
    scheduled_rules_deployment_crontab = models.ForeignKey(CrontabSchedule, blank=True, null=True,
                                                           on_delete=models.CASCADE)
    scheduled_deploy = models.BooleanField(default=False)
    file = models.FileField(name='file', upload_to='tmp/source/' + str(time.time()), blank=True)
    type = models.CharField(max_length=100, blank=True, default='', editable=False)

    def __str__(self):
        return self.uri

    @classmethod
    def get_by_uri(cls, uri):
        try:
            obj = cls.objects.get(uri=uri)
        except cls.DoesNotExist as e:
            logger.debug('Tries to access an object that does not exist : ' + str(e))
            return None
        return obj
