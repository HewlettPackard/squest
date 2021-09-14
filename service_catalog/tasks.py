import logging

from celery import shared_task
from django.core import management
from django.core.mail import EmailMultiAlternatives

from .models import TowerServer, Request

logger = logging.getLogger(__name__)


@shared_task()
def sync_tower(tower_id, job_template_id=None):
    if job_template_id is None:
        logger.info(f"[sync_tower] sync tower server with id: {tower_id}")
    else:
        logger.info(f"[sync_tower] sync one job template({job_template_id}) in tower server with id: {tower_id}")
    tower_server = TowerServer.objects.get(id=tower_id)
    tower_server.sync(job_template_id)


@shared_task()
def check_tower_job_status_task(request_id):
    logger.info(f"[check_tower_job_status_task] check Tower job status for request id: {request_id}")
    target_request = Request.objects.get(id=request_id)
    target_request.check_job_status()


@shared_task()
def send_email(subject, plain_text, html_template, from_email, receivers, reply_to):
    """
    Pass-through method so we use Celery async
    """
    msg = EmailMultiAlternatives(subject, plain_text, from_email, receivers, reply_to=reply_to)
    msg.attach_alternative(html_template, "text/html")
    msg.send()


@shared_task
def perform_backup():
    logger.info("Execute database backup")
    management.call_command('dbbackup', '--clean')
    logger.info("Database backup complete")
    logger.info("Execute media backup")
    management.call_command('mediabackup', '--clean')
    logger.info("Database media complete")
