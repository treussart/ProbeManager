from django.contrib.auth.models import User, Group
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from rest_framework import serializers

from core.models import Server, SshKey, Configuration, Job


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class PeriodicTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodicTask
        fields = "__all__"


class CrontabScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrontabSchedule
        fields = "__all__"


class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = "__all__"


class SshKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = SshKey
        fields = "__all__"


class ConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configuration
        fields = "__all__"


class ConfigurationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configuration
        fields = ('value', )


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = "__all__"
