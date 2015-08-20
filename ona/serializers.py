from rest_framework import serializers

from .models import Submission

class SubmissionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Submission
        fields = ('url', 'id', 'integration', 'report', 'content',
            'created_at', 'submitted', 'metadata')
