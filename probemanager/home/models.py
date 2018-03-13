import logging

from django.db import models
from django.utils import timezone
from django_celery_beat.models import CrontabSchedule

from home.ssh import execute
from .modelsmixins import CommonMixin


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
        return self.name + ' - ' + self.host + ', Os : ' + str(self.os)

    @classmethod
    def get_by_host(cls, host):
        try:
            host = cls.objects.get(host=host)
        except cls.DoesNotExist as e:
            cls.get_logger().debug('Tries to access an object that does not exist : ' + str(e))
            return None
        return host

    def test(self):
        command = "cat /etc/hostname"
        tasks = {"test": command}
        try:
            response = execute(self, tasks)
        except Exception as e:
            self.get_logger().error(str(e))
            return False
        logger.debug("output : " + str(response))
        return True

    def test_root(self):
        command = "service ssh status"
        tasks = {"test_root": command}
        try:
            response = execute(self, tasks, become=True)
        except Exception as e:
            logger.error(str(e))
            return False
        logger.debug("output : " + str(response))
        return True


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

    def __str__(self):
        return self.name

    def uptime(self):
        if self.server.os.name == 'debian':
            command = "ps -eo lstart\=,cmd | grep " + self.type.lower() + " | sed -n '3 p'  |  cut -d '/' -f 1"
        else:
            raise Exception("Not yet implemented")
        tasks = {"uptime": command}
        try:
            response = execute(self.server, tasks)
        except Exception as e:
            logger.error(str(e))
            return 'Failed to get the uptime on the host : ' + str(e)
        logger.debug("output : " + str(response))
        return response['uptime']

    def restart(self):
        if self.server.os.name == 'debian':
            command = "service " + self.__class__.__name__.lower() + " restart"
        else:
            raise Exception("Not yet implemented")
        tasks = {"restart": command}
        try:
            response = execute(self.server, tasks, become=True)
        except Exception as e:
            self.get_logger().error(str(e))
            return {'status': False, 'errors': str(e)}
        self.get_logger().debug("output : " + str(response))
        return {'status': True}

    def start(self):
        if self.server.os.name == 'debian':
            command = "service " + self.__class__.__name__.lower() + " start"
        else:
            raise Exception("Not yet implemented")
        tasks = {"start": command}
        try:
            response = execute(self.server, tasks, become=True)
        except Exception as e:
            self.get_logger().error(str(e))
            return {'status': False, 'errors': str(e)}
        self.get_logger().debug("output : " + str(response))
        return {'status': True}

    def stop(self):
        if self.server.os.name == 'debian':
            command = "service " + self.__class__.__name__.lower() + " stop"
        else:
            raise Exception("Not yet implemented")
        tasks = {"stop": command}
        try:
            response = execute(self.server, tasks, become=True)
        except Exception as e:
            self.get_logger().error(str(e))
            return {'status': False, 'errors': str(e)}
        self.get_logger().debug("output : " + str(response))
        return {'status': True}

    def status(self):
        if self.server.os.name == 'debian':
            command = "service " + self.__class__.__name__.lower() + " status"
        else:
            raise Exception("Not yet implemented")
        tasks = {"status": command}
        try:
            response = execute(self.server, tasks, become=True)
        except Exception as e:
            self.get_logger().error('Failed to get status : ' + str(e))
            return 'Failed to get status : ' + str(e)
        self.get_logger().debug("output : " + str(response))
        return response['status']

    def reload(self):
        if self.server.os.name == 'debian':
            command = "service " + self.__class__.__name__.lower() + " reload"
        else:
            raise Exception("Not yet implemented")
        tasks = {"reload": command}
        try:
            response = execute(self.server, tasks, become=True)
        except Exception as e:
            self.get_logger().error(str(e))
            return {'status': False, 'errors': str(e)}
        self.get_logger().debug("output : " + str(response))
        return {'status': True}

    def install(self):
        if self.server.os.name == 'debian':
            command1 = "apt update"
            command2 = "apt install " + self.__class__.__name__.lower()
        else:
            raise Exception("Not yet implemented")
        tasks = {"update": command1, "install": command2}
        try:
            response = execute(self.server, tasks, become=True)
        except Exception as e:
            self.get_logger().error(str(e))
            return {'status': False, 'errors': str(e)}
        self.get_logger().debug("output : " + str(response))
        return {'status': True}

    def update(self):
        return self.install()

    @classmethod
    def get_by_name(cls, name):
        try:
            probe = cls.objects.get(name=name)
        except cls.DoesNotExist as e:
            cls.get_logger().debug('Tries to access an object that does not exist : ' + str(e))
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
    # General
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
