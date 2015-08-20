from rest_framework import serializers

from .models import Submission

class SubmissionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Submission
        fields = ('url', 'id', 'integration', 'report', 'content',
            'created_at', 'submitted', 'metadata')

class InboundSubmissionSerializer(serializers.ModelSerializer):
    """
        Only used for posting from normal users to the default ona integration
        on the account. Model, not HyperlinkedModelSerializer
    """
    class Meta:
        model = Submission
        fields = ('id', 'integration', 'report', 'content', 'created_at',
            'submitted', 'metadata')
