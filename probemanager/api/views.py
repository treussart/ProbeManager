from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rules.models import ClassType
from api.serializers import UserSerializer, GroupSerializer, ClassTypeSerializer
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin


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


class ClassTypeViewSet(ListModelMixin, RetrieveModelMixin, viewsets.GenericViewSet):
    """
    API endpoint that allows class type to be viewed or edited. ex : Not Suspicious Traffic
    """
    queryset = ClassType.objects.all()
    serializer_class = ClassTypeSerializer
