from unittest import mock

from django_celery_beat.models import PeriodicTask, CrontabSchedule

from service_catalog.celery_beat_scheduler import DatabaseSchedulerWithCleanup
from tests.test_service_catalog.base import BaseTest

from service_catalog.celery import app


class TestCeleryBeatScheduler(BaseTest):

    @mock.patch('django_celery_beat.schedulers.DatabaseScheduler.setup_schedule')
    def test_setup_schedule(self, mock_scheduler):
        # create tasks
        crontab = CrontabSchedule.objects.create(minute=0, hour=5)
        PeriodicTask.objects.create(name="test-periodic", crontab=crontab)
        self.assertTrue(PeriodicTask.objects.filter(name="test-periodic").exists())
        app.conf.update(CELERY_ALWAYS_EAGER=True)
        # execute the cleaner. The ghost task should be deleted
        DatabaseSchedulerWithCleanup(app)
        self.assertFalse(PeriodicTask.objects.filter(name="test-periodic").exists())
        mock_scheduler.assert_called()
