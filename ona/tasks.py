from celery.task import Task
from celery.utils.log import get_task_logger
from celery.exceptions import SoftTimeLimitExceeded
from django.core.exceptions import ObjectDoesNotExist
from go_http.send import HttpApiSender
import requests, base64, json
from requests.exceptions import HTTPError
from .models import Submission

try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser

logger = get_task_logger(__name__)

class Send_Submission(Task):

    """
    Task to load and construct submission and send it off
    """
    name = "ona.tasks.send_submission"

    class FailedEventRequest(Exception):

        """
        The attempted task failed because of a non-200 HTTP return code.
        """

    def run(self, submission_id, **kwargs):
        try:
            submission = Submission.objects.get(pk=submission_id)
            if submission.submitted is False:
                integration = submission.integration.details
                data = '{"submission": '+submission.content+', "id": "'+integration["form_id"]+'"}'
                print data
                base64string = base64.encodestring(
                    '%s:%s' % (integration["username"],
                    integration["password"])).replace('\n', ''
                )
                try:
                    r = requests.post(
                        integration["url"],
                        data=data,
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": "Basic %s" % base64string
                        }
                    )
                    print json.dumps(r.json())

                except HTTPError as e:
                    #retry message sending if in 500 range (3 default retries)
                    if 500 < e.response.status_code < 599:
                        raise self.retry(exc=e)
                    else:
                        raise e
        except ObjectDoesNotExist:
            logger.error('Missing Submission object', exc_info=True)

        except SoftTimeLimitExceeded:
            logger.error (
            'Soft time limit exceed processing sending message via \
                Celery.',
            exc_info=True)

send_submission = Send_Submission()
