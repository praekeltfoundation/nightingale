from django.contrib.auth.models import User, Group
from .models import Project, UserProject, Integration
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from .serializers import (UserSerializer, GroupSerializer,
                          ProjectSerializer, UserProjectSerializer,
                          IntegrationSerializer)


class UserViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = (IsAdminUser,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows groups to be viewed or edited.
    """
    permission_classes = (IsAdminUser,)
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class ProjectViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows Project models to be viewed or edited.
    """
    permission_classes = (IsAdminUser,)
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class UserProjectViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows UserProject models to be viewed or edited.
    """
    permission_classes = (IsAdminUser,)
    queryset = UserProject.objects.all()
    serializer_class = UserProjectSerializer


class IntegrationViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows Integration models to be viewed or edited.
    """
    permission_classes = (IsAdminUser,)
    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer
