from django.contrib.auth.models import User, Group
from .models import Project, UserProject
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import (UserSerializer, GroupSerializer,
                          ProjectSerializer, UserProjectSerializer)


class UserViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class ProjectViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows Project models to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class UserProjectViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows UserProject models to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    queryset = UserProject.objects.all()
    serializer_class = UserProjectSerializer
