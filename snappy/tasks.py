from celery.task import Task
from celery.utils.log import get_task_logger
from celery.exceptions import SoftTimeLimitExceeded
from django.core.exceptions import ObjectDoesNotExist
from go_http.send import HttpApiSender
from besnappy import SnappyApiSender
from requests.exceptions import HTTPError
from .models import Message

try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser


logger = get_task_logger(__name__)


class MLStripper(HTMLParser):

    def __init__(self):
        self.convert_charrefs = False
        self.strict = False
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def handle_charref(self, name):
        pass

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


class Send_Message(Task):

    """
    Task to load and contruct message and send them off
    """
    name = "snappy.tasks.send_message"

    class FailedEventRequest(Exception):

        """
        The attempted task failed because of a non-200 HTTP return
        code.
        """

    def vumi_client(self, vumisettings):
        return HttpApiSender(
            api_url=vumisettings["vumi_api_url"],
            account_key=vumisettings["vumi_account_key"],
            conversation_key=vumisettings["vumi_conversation_key"],
            conversation_token=vumisettings["vumi_conversation_token"]
        )

    def snappy_client(self, snappysettings):
        return SnappyApiSender(
            api_key=snappysettings["snappy_api_key"],
            api_url=snappysettings["snappy_api_url"]
        )

    def run(self, message_id, **kwargs):
        """
        Load and contruct message and send them off
        """
        l = self.get_logger(**kwargs)

        l.info("Loading Message")
        try:
            message = Message.objects.get(pk=message_id)
            if message.delivered is False:  # Don't attempt to redeliver
                integration = message.integration.details
                if message.target == "VUMI":
                    vumiapi = self.vumi_client(integration)
                    try:
                            # Plain content
                        vumiresponse = vumiapi.send_text(
                            message.to_addr,
                            strip_tags(message.message))
                        l.info("Sent text message to <%s>" % message.to_addr)
                        message.metadata["vumi_message_id"] = \
                            vumiresponse["message_id"]
                        message.delivered = True
                        message.save()
                    except HTTPError as e:
                        # retry message sending if in 500 range (3 default
                        # retries)
                        if 500 < e.response.status_code < 599:
                            raise self.retry(exc=e)
                        else:
                            raise e
                    return vumiresponse
                else:
                    snappyapi = self.snappy_client(integration)
                    try:
                        # Send message
                        subject = "Report from %s" % (message.from_addr)
                        # from_email should be "user+%s@domain.org"
                        from_addr = \
                            integration["snappy_from_email"] % message.id
                        snappy_ticket = snappyapi.create_note(
                            mailbox_id=integration["snappy_mailbox_id"],
                            subject=subject,
                            message=message.message,
                            to_addr=None,
                            from_addr=[
                                {"name": message.from_addr,
                                 "address": from_addr}]
                        )
                        report = message.report
                        report.metadata["snappy_nonce"] = snappy_ticket
                        report.save()  # save the upstream report
                        message.delivered = True
                        message.save()  # save the message
                    except HTTPError as e:
                        # retry message sending if in 500 range (3 default
                        # retries)
                        if 500 < e.response.status_code < 599:
                            raise self.retry(exc=e)
                        else:
                            raise e
        except ObjectDoesNotExist:
            logger.error('Missing Message object', exc_info=True)

        except SoftTimeLimitExceeded:
            logger.error(
                'Soft time limit exceed processing location search \
                 via Celery.',
                exc_info=True)

send_message = Send_Message()
