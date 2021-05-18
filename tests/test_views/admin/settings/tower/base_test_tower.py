from django_celery_results.models import TaskResult

from service_catalog.models import Request, Instance, TowerServer
from tests.base import BaseTest


class BaseTestTower(BaseTest):

    def setUp(self):
        super(BaseTestTower, self).setUp()

        self.test_task_result = TaskResult.objects.create()
