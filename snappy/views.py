from .models import Message
from reports.models import Report
from accounts.models import UserProject, Integration
from rest_framework import viewsets, generics, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.views import APIView
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


class SnappyWebhookListener(APIView):

    """
    Triggers a send for the next subscription message
    """
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        """
        Validates webhook data before creating Outbound message
        """
        allowed_events = ['message.outgoing']
        # Look up action first
        event = request.body["event"]
        if event in allowed_events:
            if event == "message.outgoing":
                # create Vumi bound message if we can find related inbound
                nonce = request.body["note"]["ticket"]["nonce"]
                # should only be one with this nonce, but lets be liberal
                reports = Report.objects.filter(
                    metadata__contains={"snappy_nonce": nonce})
                if reports.count() > 0:
                    report = reports[0]  # if more than one, just use 1st
                    active_snappy = report.project.integrations.filter(
                        integration_type='Snappy', active=True)
                    message = Message()
                    message.integration = active_snappy[0]
                    message.report = report
                    message.target = "VUMI"
                    message.message = request.body["note"]["content"]
                    message.contact_key = report.contact_key
                    message.to_addr = report.to_addr
                    message.save()
                    # increment the replies
                    if "snappy_replies" in report.metadata:
                        report.metadata["snappy_replies"] = int(
                            report.metadata["snappy_replies"]) + 1
                    else:
                        report.metadata["snappy_replies"] = 1
                    report.save()
                    # Return
                    status = 200
                    accepted = {"accepted": True}
                else:
                    # Accept it to stop Snappy retries but do nothing ATM
                    # TODO: log failure of match
                    status = 200
                    accepted = {"accepted": True}
        else:
            # not a hook we listen to at the moment
            status = 400
            accepted = {"accepted": False,
                        "reason": "Webhook event not in allowed_events"}
        return Response(accepted, status=status)
