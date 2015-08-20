import json
from .models import Submission
from reports.models import Report
from accounts.models import UserProject, Integration
from rest_framework import viewsets, generics, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.views import APIView
from .serializers import (SubmissionSerializer,
                            InboundSubmissionSerializer)

class SubmissionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows submissions to be viewed or edited.
    """
    permission_classes = (IsAdminUser,)
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer

class OnaSubmissionPost(mixins.CreateModelMixin, generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Submission.objects.all()
    serializer_class = InboundSubmissionSerializer

    def post(self, request, *args, **kwargs):
        # load the users project - posting users should only have one project
        userprojects = UserProject.objects.get(user=self.request.user)
        project = userprojects.projects.all()[0]
        # load the ona integration - should only be one per project
        integration = Integration.objects.get(project=project,
                                                integration_type='Ona')
        request.data["integration"] = integration.id
        return self.create(request, *args, **kwargs)
