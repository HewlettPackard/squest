import logging

from celery import shared_task

from .mail_utils import django_send_email
from .models import TowerServer, Request

logger = logging.getLogger(__name__)


@shared_task()
def sync_tower(tower_id):
    logger.info("[sync_tower] sync tower server with id: {}".format(tower_id))
    tower_server = TowerServer.objects.get(id=tower_id)
    tower_server.sync()


@shared_task()
def check_tower_job_status_task(request_id):
    logger.info("[check_tower_job_status_task] check Tower job status for request id: {}".format(request_id))
    target_request = Request.objects.get(id=request_id)
    target_request.check_job_status()


@shared_task()
def send_email(subject, plain_text, html_template, from_email, receivers, reply_to):
    """
    Pass-through method so we use Celery async
    """
    django_send_email(subject, plain_text, html_template, from_email, receivers, reply_to)
