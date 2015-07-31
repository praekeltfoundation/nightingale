from rest_framework import serializers

from .models import Message


class MessageSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Message
        fields = ('url', 'id', 'integration', 'report', 'target',
                  'message', 'contact_key', 'from_addr', 'to_addr',
                  'delivered', 'metadata')


class InboundMessageSerializer(serializers.ModelSerializer):
    """
        Only used for posting from normal users to the default snappy
        integration on the account. Model, not HyperlinkedModelSerializer
    """

    class Meta:
        model = Message
        fields = ('id', 'integration', 'report', 'target',
                  'message', 'contact_key', 'from_addr', 'to_addr',
                  'delivered', 'metadata')
