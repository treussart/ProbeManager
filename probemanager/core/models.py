import logging
from collections import OrderedDict

from django.db import models
from django.utils import timezone
from django_celery_beat.models import CrontabSchedule

from .modelsmixins import CommonMixin
from .ssh import execute
from .utils import encrypt

logger = logging.getLogger(__name__)


class Job(CommonMixin, models.Model):
    STATUS_CHOICES = (
        ('In progress', 'In progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Error', 'Error'),
    )
    name = models.CharField(max_length=255)
    probe = models.CharField(max_length=255, verbose_name="Probe / URL")
    status = models.CharField(max_length=255, choices=STATUS_CHOICES)
    result = models.TextField(null=True, default=None, editable=False)
    created = models.DateTimeField(default=timezone.now)
    completed = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.name

    def get_duration(self):
        return self.created - self.completed

    @classmethod
    def create_job(cls, name, probe_name):
        job = Job(name=name, probe=probe_name, status='In progress', created=timezone.now())
        job.save()
        return job

    def update_job(self, result, status):
        self.result = result
        self.status = status
        self.completed = timezone.now()
        self.save()


class OsSupported(CommonMixin, models.Model):
    """
    Set of operating system name. For now, just debian is available.
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class SshKey(models.Model):
    """
    Set of Ssh keys, To connect to the remote server.
    """
    name = models.CharField(max_length=400, unique=True, blank=False, null=False)
    file = models.FileField(upload_to='ssh_keys/')

    def __str__(self):
        return self.name


class Server(CommonMixin, models.Model):
    """
    Server on which is deployed the Probes.
    """
    name = models.CharField(max_length=400, unique=True, default="")
    host = models.CharField(max_length=400, unique=True, default="localhost")
    os = models.ForeignKey(OsSupported, default=0, on_delete=models.CASCADE)
    remote_user = models.CharField(max_length=400, blank=True, default='admin')
    remote_port = models.IntegerField(blank=True, default=22)
    ssh_private_key_file = models.ForeignKey(SshKey, on_delete=models.CASCADE)
    become = models.BooleanField(default=False, blank=True)
    become_method = models.CharField(max_length=400, blank=True, default='sudo')
    become_user = models.CharField(max_length=400, blank=True, default='root')
    become_pass = models.CharField(max_length=400, blank=True, null=True)

    def __str__(self):
        return str(self.name) + ' - ' + str(self.host) + ', Os : ' + str(self.os)

    def save(self, **kwargs):
        if self.become_pass:
            self.become_pass = encrypt(self.become_pass)
        super().save(**kwargs)

    def test(self):
        command = "cat /etc/hostname"
        tasks = {"test_connection": command}
        try:
            response = execute(self, tasks)
        except Exception as e:
            logger.exception("Error during the connection to the server.")
            return {'status': False, 'errors': str(e)}
        logger.debug("output : " + str(response))
        return {'status': True}

    def test_become(self):
        command = "service ssh status"
        tasks = {"test_connection_and_become": command}
        try:
            response = execute(self, tasks, become=True)
        except Exception as e:
            logger.exception("Error during the connection to the server.")
            return {'status': False, 'errors': str(e)}
        logger.debug("output : " + str(response))
        return {'status': True}


class Probe(CommonMixin, models.Model):
    """
    A probe is an IDS.
    """
    # General
    name = models.CharField(max_length=400, unique=True, blank=False, null=False)
    description = models.CharField(max_length=400, blank=True, default="")
    created_date = models.DateTimeField(default=timezone.now, editable=False)
    rules_updated_date = models.DateTimeField(blank=True, null=True, editable=False)
    type = models.CharField(max_length=400, blank=True, default='', editable=False)
    subtype = models.CharField(max_length=400, blank=True, null=True, editable=False)
    secure_deployment = models.BooleanField(default=True)
    scheduled_rules_deployment_enabled = models.BooleanField(default=False)
    scheduled_rules_deployment_crontab = models.ForeignKey(CrontabSchedule, related_name='crontabschedule_rules',
                                                           blank=True, null=True, on_delete=models.CASCADE)
    scheduled_check_enabled = models.BooleanField(default=True)
    scheduled_check_crontab = models.ForeignKey(CrontabSchedule, related_name='crontabschedule_check', blank=True,
                                                null=True, on_delete=models.CASCADE)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    installed = models.BooleanField('Probe Already installed', default=False)

    def __str__(self):
        return self.name

    def uptime(self):
        if self.installed:
            if self.server.os.name == 'debian' or self.server.os.name == 'ubuntu':
                command = "service " + self.type.lower() + " status | grep since"
            else:  # pragma: no cover
                raise NotImplementedError
            tasks = {"uptime": command}
            try:
                response = execute(self.server, tasks, become=True)
            except Exception as e:
                logger.exception("Error during the uptime")
                return 'Failed to get the uptime on the host : ' + str(e)
            logger.debug("output : " + str(response))
            return response['uptime']
        else:
            return 'Not installed'

    def restart(self):
        if self.server.os.name == 'debian' or self.server.os.name == 'ubuntu':
            command = "service " + self.__class__.__name__.lower() + " restart"
        else:  # pragma: no cover
            raise NotImplementedError
        tasks = {"restart": command}
        try:
            response = execute(self.server, tasks, become=True)
        except Exception:
            logger.exception("Error during restart")
            return {'status': False, 'errors': "Error during restart"}
        logger.debug("output : " + str(response))
        return {'status': True}

    def start(self):
        if self.server.os.name == 'debian' or self.server.os.name == 'ubuntu':
            command = "service " + self.__class__.__name__.lower() + " start"
        else:  # pragma: no cover
            raise NotImplementedError
        tasks = {"start": command}
        try:
            response = execute(self.server, tasks, become=True)
        except Exception:
            logger.exception("Error during start")
            return {'status': False, 'errors': "Error during start"}
        logger.debug("output : " + str(response))
        return {'status': True}

    def stop(self):
        if self.server.os.name == 'debian' or self.server.os.name == 'ubuntu':
            command = "service " + self.__class__.__name__.lower() + " stop"
        else:  # pragma: no cover
            raise NotImplementedError
        tasks = {"stop": command}
        try:
            response = execute(self.server, tasks, become=True)
        except Exception:
            logger.exception("Error during stop")
            return {'status': False, 'errors': "Error during stop"}
        logger.debug("output : " + str(response))
        return {'status': True}

    def status(self):
        if self.installed:
            if self.server.os.name == 'debian' or self.server.os.name == 'ubuntu':
                command = "service " + self.__class__.__name__.lower() + " status"
            else:  # pragma: no cover
                raise NotImplementedError
            tasks = {"status": command}
            try:
                response = execute(self.server, tasks, become=True)
            except Exception:
                logger.exception('Failed to get status')
                return 'Failed to get status'
            logger.debug("output : " + str(response))
            return response['status']
        else:
            return " "

    def reload(self):
        if self.server.os.name == 'debian' or self.server.os.name == 'ubuntu':
            command = "service " + self.__class__.__name__.lower() + " reload"
        else:  # pragma: no cover
            raise NotImplementedError
        tasks = {"reload": command}
        try:
            response = execute(self.server, tasks, become=True)
        except Exception:
            logger.exception("Error during reload")
            return {'status': False, 'errors': "Error during reload"}
        logger.debug("output : " + str(response))
        return {'status': True}

    def install(self, version=None):  # pragma: no cover
        if self.server.os.name == 'debian' or self.server.os.name == 'ubuntu':
            command1 = "apt update"
            command2 = "apt install " + self.__class__.__name__.lower()
        else:  # pragma: no cover
            raise NotImplementedError
        tasks = OrderedDict(sorted({"1_update": command1, "2_install": command2}.items(), key=lambda t: t[0]))
        try:
            response = execute(self.server, tasks, become=True)
            self.installed = True
            self.save()
        except Exception:
            logger.exception("Error during install")
            return {'status': False, 'errors': "Error during install"}
        logger.debug("output : " + str(response))
        return {'status': True}

    def update(self, version=None):  # pragma: no cover
        return self.install(version=version)

    @classmethod
    def get_by_name(cls, name):
        try:
            probe = cls.objects.get(name=name)
        except cls.DoesNotExist as e:
            logger.debug('Tries to access an object that does not exist : ' + str(e))
            return None
        return probe


class ProbeConfiguration(CommonMixin, models.Model):
    """
    Configuration for a probe, Allows you to reuse the configuration.
    """
    # General
    name = models.CharField(max_length=100, unique=True, blank=False, null=False)

    def __str__(self):
        return self.name


class Configuration(models.Model):
    """
    Configuration for the application.
    """
    key = models.CharField(max_length=100, unique=True, blank=False, null=False)
    value = models.CharField(max_length=300, blank=True, null=False)

    def __str__(self):
        return self.key

    @classmethod
    def get_value(cls, key):
        try:
            if cls.objects.get(key=key):
                if cls.objects.get(key=key).value != "":
                    return cls.objects.get(key=key).value
                else:
                    return None
            else:
                return None
        except cls.DoesNotExist:
            return None
