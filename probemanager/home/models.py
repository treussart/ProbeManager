from django.db import models
from django.utils import timezone
from django_celery_beat.models import CrontabSchedule
import logging
# from home.ansible_tasks import execute
from home.ssh import execute


logger = logging.getLogger(__name__)


class Job(models.Model):
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
    def get_all(cls):
        return cls.objects.all()

    @classmethod
    def get_last(cls, nbr):
        return cls.objects.all()[:nbr]

    @classmethod
    def get_by_id(cls, id):
        try:
            object = cls.objects.get(id=id)
        except cls.DoesNotExist as e:
            logger.debug('Tries to access an object that does not exist : ' + e.__str__())
            return None
        return object

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


class OsSupported(models.Model):
    """
    Set of operating system name. For now, just debian is available.
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    @classmethod
    def get_by_id(cls, id):
        try:
            object = cls.objects.get(id=id)
        except cls.DoesNotExist as e:
            logger.debug('Tries to access an object that does not exist : ' + e.__str__())
            return None
        return object


class SshKey(models.Model):
    """
    Set of Ssh keys, To connect to the remote server in Ansible.
    """
    name = models.CharField(max_length=400, unique=True, blank=False, null=False)
    file = models.FileField(upload_to='ssh_keys/')

    def __str__(self):
        return self.name


class Server(models.Model):
    """
    Server on which is deployed the Probes.
    """
    name = models.CharField(max_length=400, unique=True, default="")
    host = models.CharField(max_length=400, unique=True, default="localhost")
    os = models.ForeignKey(OsSupported, default=0)
    # Ansible
    ansible_remote_user = models.CharField(max_length=400, blank=True, default='admin')
    ansible_remote_port = models.IntegerField(blank=True, default=22)
    ansible_ssh_private_key_file = models.ForeignKey(SshKey, blank=True, null=True)
    # Not Yet implemented in Inventory in API Python
    # ansible_host_key_checking = models.BooleanField(default=True, blank=True)
    ansible_become = models.BooleanField(default=False, blank=True)
    ansible_become_method = models.CharField(max_length=400, blank=True, default='sudo')
    ansible_become_user = models.CharField(max_length=400, blank=True, default='root')
    ansible_become_pass = models.CharField(max_length=400, blank=True, null=True)

    def __str__(self):
        return self.name + ' - ' + self.host

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    @classmethod
    def get_by_id(cls, id):
        try:
            probe = cls.objects.get(id=id)
        except cls.DoesNotExist as e:
            logger.debug('Tries to access an object that does not exist : ' + e.__str__())
            return None
        return probe

    @classmethod
    def get_by_host(cls, host):
        try:
            host = cls.objects.get(host=host)
        except cls.DoesNotExist as e:
            logger.debug('Tries to access an object that does not exist : ' + e.__str__())
            return None
        return host

    def test(self):
        command = "cat /etc/hostname"
        tasks = {"test": command}
        try:
            response = execute(self, tasks)
        except Exception as e:
            logger.error(e.__str__())
            return False
        logger.debug("output : " + str(response))
        return True

    def test_root(self):
        command = "service ssh status"
        tasks = {"test_root": command}
        try:
            response = execute(self, tasks, become=True)
        except Exception as e:
            logger.error(e.__str__())
            return False
        logger.debug("output : " + str(response))
        return True


class Probe(models.Model):
    """
    A probe is an IDS.
    """
    # General
    name = models.CharField(max_length=400, unique=True, blank=False, null=False)
    description = models.CharField(max_length=400, blank=True, default="")
    created_date = models.DateTimeField(default=timezone.now, editable=False)
    rules_updated_date = models.DateTimeField(blank=True, null=True, editable=False)
    type = models.CharField(max_length=400, blank=True, default='', editable=False)
    secure_deployment = models.BooleanField(default=True)
    scheduled_enabled = models.BooleanField('Enabled scheduled deployment of rules', default=False)
    scheduled_crontab = models.ForeignKey(CrontabSchedule, blank=True, null=True, verbose_name='Scheduled Crontab (Only the first time)')
    server = models.ForeignKey(Server)

    def __str__(self):
        return self.name

    def uptime(self):
        command = "ps -eo lstart\=,cmd | grep " + self.type.lower() + " | sed -n '1 p'  |  cut -d '/' -f 1"
        tasks = {"uptime": command}
        try:
            response = execute(self.server, tasks)
        except Exception as e:
            logger.error(e.__str__())
            return 'Failed to get the uptime on the host : ' + str(e)
        logger.debug("output : " + str(response))
        return response['uptime']

    def restart(self):
        command = "service " + self.__class__.__name__.lower() + " restart"
        tasks = {"restart": command}
        try:
            response = execute(self.server, tasks, become=True)
        except Exception as e:
            logger.error(e.__str__())
            return False
        logger.debug("output : " + str(response))
        return True

    def start(self):
        command = "service " + self.__class__.__name__.lower() + " start"
        tasks = {"start": command}
        try:
            response = execute(self.server, tasks, become=True)
        except Exception as e:
            logger.error(e.__str__())
            return False
        logger.debug("output : " + str(response))
        return True

    def stop(self):
        command = "service " + self.__class__.__name__.lower() + " stop"
        tasks = {"stop": command}
        try:
            response = execute(self.server, tasks, become=True)
        except Exception as e:
            logger.error(e.__str__())
            return False
        logger.debug("output : " + str(response))
        return True

    def status(self):
        command = "service " + self.__class__.__name__.lower() + " status"
        tasks = {"status": command}
        try:
            response = execute(self.server, tasks, become=True)
        except Exception as e:
            logger.error('Failed to get status : ' + e.__str__())
            return 'Failed to get status : ' + e.__str__()
        logger.debug("output : " + str(response))
        return response['status']

    def reload(self):
        command = "service " + self.__class__.__name__.lower() + " reload"
        tasks = {"reload": command}
        try:
            response = execute(self.server, tasks, become=True)
        except Exception as e:
            logger.error(e.__str__())
            return False
        logger.debug("output : " + str(response))
        return True

    def install(self):
        command1 = "apt update"
        command2 = "apt install " + self.__class__.__name__.lower()
        tasks = {"update": command1, "install": command2}
        try:
            response = execute(self.server, tasks, become=True)
        except Exception as e:
            logger.error(e.__str__())
            return False
        logger.debug("output : " + str(response))
        return True

    def update(self):
        return self.install()

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    @classmethod
    def get_by_id(cls, id):
        try:
            probe = cls.objects.get(id=id)
        except cls.DoesNotExist as e:
            logger.debug('Tries to access an object that does not exist : ' + e.__str__())
            return None
        return probe

    @classmethod
    def get_by_name(cls, name):
        try:
            probe = cls.objects.get(name=name)
        except cls.DoesNotExist as e:
            logger.debug('Tries to access an object that does not exist : ' + e.__str__())
            return None
        return probe


class ProbeConfiguration(models.Model):
    """
    Configuration for a probe, Allows you to reuse the configuration.
    """
    # General
    name = models.CharField(max_length=100, unique=True, blank=False, null=False)

    def __str__(self):
        return self.name

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    @classmethod
    def get_by_id(cls, id):
        try:
            object = cls.objects.get(id=id)
        except cls.DoesNotExist as e:
            logger.debug('Tries to access an object that does not exist : ' + e.__str__())
            return None
        return object


class Configuration(models.Model):
    """
    Configuration for the application.
    """
    # General
    key = models.CharField(max_length=100, unique=True, blank=False, null=False)
    value = models.CharField(max_length=300, blank=False, null=False)

    def __str__(self):
        return self.key

    @classmethod
    def get_value(cls, key):
        if cls.objects.get(key=key):
            if cls.objects.get(key=key).value:
                return cls.objects.get(key=key).value
            else:
                return None
        else:
            return None
