from celery.task import Task
from celery.utils.log import get_task_logger
from celery.exceptions import SoftTimeLimitExceeded
from django.core.exceptions import ObjectDoesNotExist
import requests
import json
from requests.exceptions import HTTPError
from .models import Submission

logger = get_task_logger(__name__)


class SendSubmission(Task):

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
            try:
                submission = Submission.objects.get(pk=submission_id)
            except ObjectDoesNotExist:
                logger.error('Missing Submission object', exc_info=True)

            if submission.submitted is False:
                integration = submission.integration.details
                data = json.dumps({
                    "submission": json.loads(submission.content),
                    "id": integration["form_id"]
                })
                try:
                    r = requests.post(
                        integration["url"],
                        data=data,
                        auth=(integration["username"],
                              integration["password"]),
                        headers={
                            "Content-Type": "application/json",
                        }
                    )

                    response = r.json()
                except HTTPError as e:
                    # retry message sending if in 500 range (3 default retries)
                    if 500 < e.response.status_code < 599:
                        raise self.retry(exc=e)
                    else:
                        raise e

                # Log the Ona response on the report
                report = submission.report
                if "error" in response:
                    report.metadata["ona_response"] = response["error"]
                else:
                    report.metadata["ona_response"] = response["message"]
                report.save()

                # Mark the submission as submitted
                submission.submitted = True
                submission.save()

        except SoftTimeLimitExceeded:
            logger.error(
                'Soft time limit exceed processing sending message via \
                    Celery.',
                exc_info=True)

send_submission = SendSubmission()
