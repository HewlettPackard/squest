import logging

from django.core.management import BaseCommand

from service_catalog.maintenance_jobs import cleanup_ghost_docs_images

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def __init__(self):
        super().__init__()

    def handle(self, *args, **options):
        print("[Cleanup Martor images] Start")
        cleanup_ghost_docs_images()
        print("[Cleanup Martor images] End")
