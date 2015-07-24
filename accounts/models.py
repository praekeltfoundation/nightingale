import uuid

from django.contrib.postgres.fields import HStoreField
from django.contrib.auth.models import User
from django.db import models


class Project(models.Model):

    """
    Projects collecting reports

    :param str code:
        Short name for the project. E.g. 'SHOUTZA'.

    :param str name:
        Long description. E.g. 'Shout South Africa'.

    :param dict metadata:
        A hstore field for unstructured project information.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    metadata = HStoreField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):  # __unicode__ on Python 2
        return str(self.name)


class UserProject(models.Model):

    """
    Projects a User has access to
    """
    user = models.OneToOneField(User)
    projects = models.ManyToManyField(Project)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):  # __unicode__ on Python 2
        return str(self.user.username)
