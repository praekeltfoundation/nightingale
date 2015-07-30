import uuid

from django.db import models
from accounts.models import Integration
from reports.models import Report


class Ticket(models.Model):

    """
    Ticket to sync between Vumi and Snappy

    :param fk integration:
        Link to the integration details

    :param fk report:
        Optional link to the report that triggered the ticket

    :param str support_nonce:
        Nonce from Snappy

    :param str support_id:
        ID from Snappy

    :param str message:
        Message to send over to Snappy

    :param str response:
        Reply from the Snappy reply

    :param str contact_key:
        Vumi contact_key - can be used for lookups

    :param str to_addr:
        Reporting to_addr (no expectation of type)

    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    integration = models.ForeignKey(Integration,
                                    related_name='tickets',
                                    null=False)
    report = models.ForeignKey(Report,
                               related_name='ticket',
                               null=True)
    support_nonce = models.CharField(max_length=43, null=True, blank=True)
    support_id = models.IntegerField(null=True, blank=True)
    message = models.TextField(
        verbose_name=u'Inbound Message', null=False, blank=False)
    response = models.TextField(
        verbose_name=u'Outbound Response', null=True, blank=True)
    contact_key = models.CharField(max_length=36, null=False, blank=False)
    to_addr = models.CharField(max_length=255, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s" % self.message
