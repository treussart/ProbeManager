from django.db import models
from django.utils import timezone
from django_celery_beat.models import CrontabSchedule
import logging
from home.ansible_tasks import execute


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
            logger.debug('Tries to access an object that does not exist : ' + str(e))
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
            logger.debug('Tries to access an object that does not exist : ' + str(e))
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
            logger.debug('Tries to access an object that does not exist : ' + str(e))
            return None
        return probe

    @classmethod
    def get_by_host(cls, host):
        try:
            host = cls.objects.get(host=host)
        except cls.DoesNotExist as e:
            logger.debug('Tries to access an object that does not exist : ' + str(e))
            return None
        return host

    def test(self):
        tasks = [
            dict(name="test", action=dict(module='shell', args='cat /etc/hostname')),
        ]
        return execute(self, tasks)

    def test_root(self):
        tasks = [
            dict(name="test_root", action=dict(module='shell', args='service ssh status')),
        ]
        return execute(self, tasks)


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
        tasks = [
            dict(name="uptime", action=dict(module='shell', args='ps -o lstart\= -p $( pidof ' + self.type.lower() + ' )')),
        ]
        response = execute(self.server, tasks)
        if response['result'] == 0:
            return response['message']
        else:
            return 'Failed to get the uptime on the host'

    def restart(self):
        tasks = [
            dict(name="restart", action=dict(module='service', name=self.__class__.__name__.lower(), state='restarted')),
        ]
        return execute(self.server, tasks)

    def start(self):
        tasks = [
            dict(name="start", action=dict(module='service', name=self.__class__.__name__.lower(), state='started')),
        ]
        return execute(self.server, tasks)

    def stop(self):
        tasks = [
            dict(name="stop", action=dict(module='service', name=self.__class__.__name__.lower(), state='stopped')),
        ]
        return execute(self.server, tasks)

    def status(self):
        tasks = [
            dict(name="status_" + self.__class__.__name__, action=dict(module='shell', args='service ' + self.__class__.__name__.lower() + ' status')),
        ]
        return execute(self.server, tasks)

    def reload(self):
        tasks = [
            dict(name="reload_" + self.__class__.__name__, action=dict(module='shell', args='service ' + self.__class__.__name__.lower() + ' reload')),
        ]
        return execute(self.server, tasks)

    def install(self):
        tasks = [
            dict(name="install_python3-apt", action=dict(module='shell', args='apt install python3-apt')),
            dict(name="install_" + self.__class__.__name__, action=dict(module='apt', name=self.__class__.__name__.lower(), state='present')),
        ]
        return execute(self.server, tasks)

    def update(self):
        tasks = [
            dict(name="update_python3-apt", action=dict(module='shell', args='apt install python3-apt')),
            dict(name="update_" + self.__class__.__name__, action=dict(module='apt', name=self.__class__.__name__.lower(), state='latest', update_cache='yes')),
        ]
        return execute(self.server, tasks)

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    @classmethod
    def get_by_id(cls, id):
        try:
            probe = cls.objects.get(id=id)
        except cls.DoesNotExist as e:
            logger.debug('Tries to access an object that does not exist : ' + str(e))
            return None
        return probe

    @classmethod
    def get_by_name(cls, name):
        try:
            probe = cls.objects.get(name=name)
        except cls.DoesNotExist as e:
            logger.debug('Tries to access an object that does not exist : ' + str(e))
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
            logger.debug('Tries to access an object that does not exist : ' + str(e))
            return None
        return object
