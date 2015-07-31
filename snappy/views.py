from .models import Message
from accounts.models import UserProject, Integration
from rest_framework import viewsets, generics, mixins
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import (MessageSerializer,
                          InboundMessageSerializer)


class MessageViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows categories to be viewed or edited.
    """
    permission_classes = (IsAdminUser,)
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class SnappyMessagePost(mixins.CreateModelMixin, generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Message.objects.all()
    serializer_class = InboundMessageSerializer

    def post(self, request, *args, **kwargs):
        # load the users project - posting users should only have one project
        userprojects = UserProject.objects.get(user=self.request.user)
        project = userprojects.projects.all()[0]
        # load the snappy integration - should only be one per project
        integration = Integration.objects.get(project=project,
                                              integration_type='Snappy')
        request.data["integration"] = integration.id
        request.data["target"] = "SNAPPY"
        return self.create(request, *args, **kwargs)
