from django.contrib.postgres.fields import HStoreField
from django.db import models
from accounts.models import Integration
from reports.models import Report

class Submission(models.Model):

    integration = models.ForeignKey(Integration,
                                    related_name='submissions',
                                    null=False)
    report = models.ForeignKey(Report,
                                related_name='submissions',
                                null=True)
    content = models.TextField(null=False, blank=False)
    metadata = HStoreField(null=True, blank=True, default={})
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content
