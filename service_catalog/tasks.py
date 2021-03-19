import logging

from celery import shared_task

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


