import json
from .models import Submission
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from .serializers import SubmissionSerializer

class SubmissionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows submissions to be viewed.
    """
    permission_classes = (IsAdminUser,)
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
