import uuid

from django.contrib.postgres.fields import HStoreField
from django.db import models
from accounts.models import Project


class Category(models.Model):

    """
    Categories reports can me made against

    :param str name:
        Long description. E.g. 'Shout South Africa'.

    :param int order:
        Optional sort order for UI

    :param dict metadata:
        A hstore field for unstructured project information.

    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    order = models.IntegerField(default=1000)
    metadata = HStoreField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name_plural = "categories"

    def __str__(self):  # __unicode__ on Python 2
        return str(self.name)


class ProjectCategory(models.Model):

    """
    Categories a Project can report on
    """
    project = models.OneToOneField(Project)
    categories = models.ManyToManyField(Category)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "project categories"

    def __str__(self):  # __unicode__ on Python 2
        return "%s Categories" % str(self.project.code)
