from celery.task import Task
from celery.utils.log import get_task_logger
from celery.exceptions import SoftTimeLimitExceeded
from django.core.exceptions import ObjectDoesNotExist
from go_http.send import HttpApiSender
from besnappy import SnappyApiSender
import requests
import json
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
                        report = message.report
                        # from_email should be "user+%s@domain.org"
                        from_addr = \
                            integration["snappy_from_email"] % message.id
                        if "snappy_nonce" not in report.metadata:
                            # open a new ticket
                            subject = "Report from %s" % (message.from_addr)
                            snappy_ticket = snappyapi.create_note(
                                mailbox_id=integration["snappy_mailbox_id"],
                                subject=subject,
                                message=message.message,
                                to_addr=None,
                                from_addr=[
                                    {"name": message.from_addr,
                                     "address": from_addr}]
                            )
                            # Add tags
                            categories = report.categories.all()
                            tags = list(cat.name for cat in categories)
                            add_tags.delay(integration, snappy_ticket, tags)
                            # Log the snappy ticket on the report
                            report.metadata["snappy_nonce"] = snappy_ticket
                            report.save()  # save the upstream report
                        else:
                            # this is a reply to an open ticket
                            subject = "Update from %s" % (message.from_addr)
                            snappy_ticket = snappyapi.create_note(
                                mailbox_id=integration["snappy_mailbox_id"],
                                ticket_id=report.metadata["snappy_nonce"],
                                subject=subject,
                                message=message.message,
                                to_addr=None,
                                from_addr=[
                                    {"name": message.from_addr,
                                     "address": from_addr}]
                            )
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
                'Soft time limit exceed processing sending message \
                 via Celery.',
                exc_info=True)

send_message = Send_Message()


class Add_Tags(Task):

    """
    Task to add tags to tickets in Snappy
    """
    name = "snappy.tasks.add_tags"

    class FailedEventRequest(Exception):

        """
        The attempted task failed because of a non-200 HTTP return
        code.
        """

    def snappy_client(self, snappysettings):
        return SnappyApiSender(
            api_key=snappysettings["snappy_api_key"],
            api_url=snappysettings["snappy_api_url"]
        )

    def run(self, snappysettings, snappynonce, tags, **kwargs):
        """
        Load and contruct message and send them off
        """
        l = self.get_logger(**kwargs)

        l.info("Adding tags")
        try:
            url = "%s/ticket/%s/tags" % (
                snappysettings["snappy_api_url"], snappynonce)
            data = json.dumps({"tags": tags})
            headers = {'content-type': 'application/json; charset=utf-8'}
            auth = ('x', snappysettings["snappy_api_key"])
            result = requests.post(url, auth=auth, data=data,
                                   headers=headers, verify=False)
            result.raise_for_status()
            return result  # should be "OK"
        except HTTPError as e:
            # retry message sending if in 500 range (3 default
            # retries)
            if 500 < e.response.status_code < 599:
                raise self.retry(exc=e)
            else:
                raise e

        except SoftTimeLimitExceeded:
            logger.error(
                'Soft time limit exceed processing adding tags \
                 via Celery.',
                exc_info=True)

add_tags = Add_Tags()
