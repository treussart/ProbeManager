from django.contrib.auth.models import User, Group
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from rest_framework import status
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.response import Response
from django.conf import settings
import os

from core.models import Server, SshKey, Configuration
from rules.models import ClassType
from .serializers import UserSerializer, GroupSerializer, ClassTypeSerializer, CrontabScheduleSerializer, \
    PeriodicTaskSerializer, ServerSerializer, SshKeySerializer, ConfigurationSerializer, ConfigurationUpdateSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class ClassTypeViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    API endpoint that allows class type to be viewed or edited. ex : Not Suspicious Traffic
    """
    queryset = ClassType.objects.all()
    serializer_class = ClassTypeSerializer


class PeriodicTaskViewSet(viewsets.ModelViewSet):
    queryset = PeriodicTask.objects.all()
    serializer_class = PeriodicTaskSerializer


class CrontabScheduleViewSet(viewsets.ModelViewSet):
    queryset = CrontabSchedule.objects.all()
    serializer_class = CrontabScheduleSerializer


class ServerViewSet(viewsets.ModelViewSet):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer


class ConfigurationViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Configuration.objects.all()
    serializer_class = ConfigurationSerializer

    def update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, pk=None):
        conf = self.get_object()
        serializer = ConfigurationUpdateSerializer(conf, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SshKeyView(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = SshKey.objects.all()
    serializer_class = SshKeySerializer

    def create(self, request):
        with open(settings.BASE_DIR + "/ssh_keys/" + request.data['name'], 'w', encoding="utf_8") as f:
            f.write(request.data['file'])
        os.chmod(settings.BASE_DIR + "/ssh_keys/" + request.data['name'], 0o640)
        sshkey = SshKey(name=request.data['name'], file="ssh_keys/" + request.data['file'])
        sshkey.save()
        return Response(status=204)
