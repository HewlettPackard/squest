import logging

from django.db import transaction
from django_celery_beat.models import PeriodicTask
from django_celery_beat.models import PeriodicTasks
from django_celery_beat.schedulers import DatabaseScheduler

logger = logging.getLogger(__name__)


class DatabaseSchedulerWithCleanup(DatabaseScheduler):

    def setup_schedule(self):
        """
        Cleanup previous periodic tasks from the database before starting the default scheduler
        """
        schedule = self.app.conf.beat_schedule
        with transaction.atomic():
            num, info = PeriodicTask.objects.\
                exclude(task__startswith='celery.').\
                exclude(name__in=schedule.keys()).\
                delete()
            logger.info("Removed %d obsolete periodic tasks.", num)
            if num > 0:
                PeriodicTasks.update_changed()
        super(DatabaseSchedulerWithCleanup, self).setup_schedule()
