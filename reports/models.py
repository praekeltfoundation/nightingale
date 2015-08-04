import uuid

from django.contrib.postgres.fields import HStoreField
from django.contrib.gis.db import models
from django.conf import settings
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


class Location(models.Model):

    """
    Inbound reports point of location

    :param point point:
        GeoDjango point for x/y co-ordinates

    :param datetime incident_at:
        Optional explicit date of incident.

    :param dict metadata:
        A hstore field for unstructured report information.

    """
    point = models.PointField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # GeoDjango-specific overriding the default manager with a
    # GeoManager instance.
    objects = models.GeoManager()

    def __str__(self):
        return "%s" % (self.point)


class Report(models.Model):

    """
    Inbound reports of incidents

    :param str contact_key:
        Vumi contact_key

    :param str to_addr:
        Reporting to_addr (no expectation of type)

    :param str description:
        Report details, allowed to be null so category and point logs possible

    :param point location:
        GeoDjango point for x/y co-ordinates

    :param datetime incident_at:
        Optional explicit date of incident.

    :param dict metadata:
        A hstore field for unstructured report information.

    """
    contact_key = models.CharField(max_length=36, null=False, blank=False)
    to_addr = models.CharField(max_length=255, null=False, blank=False)
    categories = models.ManyToManyField(Category)
    project = models.ForeignKey(Project,
                                related_name='reports',
                                null=True)
    location = models.ForeignKey(Location,
                                 related_name='reports',
                                 null=False)
    description = models.TextField(null=True, blank=True)
    incident_at = models.DateTimeField(null=True, blank=True)
    metadata = HStoreField(null=True, blank=True, default={})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Incident for %s reported at %s" % (
            self.project.name, self.created_at)

# Make sure new messages are sent
from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import bounce_report


@receiver(post_save, sender=Report)
def fire_bounce_action(sender, instance, created, **kwargs):
    """
    first check for categories as those are manytomany and applied after 1st
    creation action.
    if description is still None then fire with 10 min delay to allow for
    user update. bounce_reports is responsible for not firing if already logged
    """
    if instance.categories.count() > 0:
        if instance.description is None:
            when = int(settings.NIGHTINGALE_BOUNCE_DELAY) * 60
        else:
            when = 0

        bounce_report.apply_async(kwargs={"report_id": instance.id},
                                  countdown=when)
