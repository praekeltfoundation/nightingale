from celery.task import Task
from celery.utils.log import get_task_logger
from celery.exceptions import SoftTimeLimitExceeded

from django.core.exceptions import ObjectDoesNotExist

logger = get_task_logger(__name__)

from .models import Report
from snappy.models import Message


class Bounce_Report(Task):

    """
    Task to load and handle where reports need to go when complete
    """
    name = "reports.tasks.bounce_report"

    class FailedEventRequest(Exception):

        """
        The attempted task failed because of a non-200 HTTP return
        code.
        """

    def run(self, report_id, **kwargs):
        """
        Load and contruct message and send them off
        """
        l = self.get_logger(**kwargs)

        l.info("Loading Report")
        try:
            report = Report.objects.get(pk=report_id)
            integrations = report.project.integrations
            categories = report.categories.all()
            active_snappy = integrations.filter(integration_type='Snappy',
                                                active=True)
            if active_snappy.count() == 1 and \
                    "snappy_nonce" not in report.metadata:
                # create a snappy message
                content = "<b>Description:</b> %s <br>" % report.description
                content += "<b>Categories:</b> <br>"
                for category in categories:
                    content += "%s <br>" % category.name
                content += '<b>Location:</b> ' + \
                    '<a href="https://www.google.co.za' +\
                    '/maps/@%s,%s,13z">Map</a>' % (
                        report.location.point.y, report.location.point.x)
                message = Message()
                message.integration = active_snappy[0]
                message.report = report
                message.target = "SNAPPY"
                message.message = content
                message.contact_key = report.contact_key
                message.from_addr = report.to_addr
                message.save()
        except ObjectDoesNotExist:
            logger.error('Missing Report object', exc_info=True)

        except SoftTimeLimitExceeded:
            logger.error(
                'Soft time limit exceed processing location search \
                 via Celery.',
                exc_info=True)

bounce_report = Bounce_Report()
