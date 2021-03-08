import logging

from celery import shared_task

from .models import TowerServer

logger = logging.getLogger(__name__)


@shared_task()
def sync_tower(tower_id):
    logger.info("[sync_tower] sync tower server with id: {}".format(tower_id))
    tower_server = TowerServer.objects.get(id=tower_id)
    tower_server.sync()

