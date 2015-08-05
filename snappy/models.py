from django.contrib.postgres.fields import HStoreField
from django.db import models
from accounts.models import Integration
from reports.models import Report


class Message(models.Model):

    """
    Message to sync between Vumi and Snappy

    :param fk integration:
        Link to the integration details

    :param fk report:
        Optional link to the report that triggered the ticket

    :param str target:
        Where the message will be delivered (VUMI or SNAPPY)

    :param str message:
        Message to send over to Snappy

    :param str contact_key:
        Optional Vumi contact_key - can be used for extras lookups

    :param str from_addr:
        Message from_addr (no expectation of type)

    :param str to_addr:
        Message to_addr (no expectation of type)

    :param dict metadata:
        A hstore field for semi-structured message information like nonce/mID

    """
    TARGET = (
        ('VUMI', 'Vumi'),
        ('SNAPPY', 'Snappy'),
    )
    integration = models.ForeignKey(Integration,
                                    related_name='messages',
                                    null=False)
    report = models.ForeignKey(Report,
                               related_name='messages',
                               null=True)
    target = models.CharField(max_length=6,
                              choices=TARGET)
    message = models.TextField(
        verbose_name=u'Message', null=False, blank=False)
    contact_key = models.CharField(max_length=36, null=True, blank=True)
    from_addr = models.CharField(max_length=255, null=True, blank=True)
    to_addr = models.CharField(max_length=255, null=True, blank=True)
    delivered = models.BooleanField(default=False)
    metadata = HStoreField(null=True, blank=True, default={})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s to %s" % (self.message, self.target)

# Make sure new messages are sent
from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import send_message


@receiver(post_save, sender=Message)
def fire_msg_action_if_new(sender, instance, created, **kwargs):
    if created:
        send_message.delay(str(instance.id))
