import logging
from smtplib import SMTPDataError, SMTPRecipientsRefused

from celery import shared_task
from django.core import management
from django.core.mail import EmailMultiAlternatives

from .maintenance_jobs import cleanup_ghost_docs_images

logger = logging.getLogger(__name__)


@shared_task()
def towerserver_sync(tower_id, job_template_id=None):
    from service_catalog.models.tower_server import TowerServer
    if job_template_id is None:
        logger.info(f"[towerserver_sync] sync tower server with id: {tower_id}")
    else:
        logger.info(f"[towerserver_sync] sync one job template({job_template_id}) in tower server with id: {tower_id}")
    tower_server = TowerServer.objects.get(id=tower_id)
    tower_server.sync(job_template_id)


@shared_task()
def check_tower_job_status_task(request_id):
    from service_catalog.models.request import Request
    logger.info(f"[check_tower_job_status_task] check Tower job status for request id: {request_id}")
    target_request = Request.objects.get(id=request_id)
    target_request.check_job_status()


@shared_task()
def send_email(subject, plain_text, html_template, from_email, receivers=None, bcc=None, reply_to=None, headers=None):
    """
    Pass-through method so we use Celery async
    """
    if not receivers and not bcc and not reply_to:
        logger.info(f"[send_email] no receivers for the email. Email not sent.")
        return
    logger.info(f"[send_email] celery task executed - subject: '{subject}',"
                f" from_email: '{from_email}',"
                f" receivers: '{receivers}',"
                f" reply_to: '{reply_to}',"
                f" bcc: '{bcc}'")
    msg = EmailMultiAlternatives(subject, plain_text, from_email, to=receivers,
                                 bcc=bcc,
                                 reply_to=reply_to,
                                 headers=headers)
    msg.attach_alternative(html_template, "text/html")
    try:
        msg.send()
        logger.info(f"[send_email] email sent")
    except SMTPDataError as e:
        logger.error(f"[send_email] Fail to send email: {e.smtp_code} {e.smtp_error}")
    except SMTPRecipientsRefused as e:
        logger.error(f"[send_email] Fail to send email to addresses: {e.recipients}")
    except ConnectionRefusedError as e:
        logger.error(f"[send_email] Fail to send email. Connection refused: {e.strerror}")


@shared_task
def perform_backup():
    logger.info("Execute database backup")
    management.call_command('dbbackup', '--clean')
    logger.info("Database backup complete")
    logger.info("Execute media backup")
    management.call_command('mediabackup', '--clean')
    logger.info("Database media complete")


@shared_task
def task_cleanup_ghost_docs_images():
    cleanup_ghost_docs_images()
