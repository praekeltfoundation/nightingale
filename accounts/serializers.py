from django.contrib.auth.models import User, Group
from .models import Project, UserProject, Integration
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Group
        fields = ('url', 'name')


class ProjectSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Project
        fields = ('url', 'id', 'code', 'name', 'metadata')


class UserProjectSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = UserProject
        fields = ('url', 'user', 'projects')


class IntegrationSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Integration
        fields = ('url', 'id', 'project', 'integration_type',
                  'details', 'active')
