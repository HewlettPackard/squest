from django_celery_results.models import TaskResult

from tests.test_service_catalog.base import BaseTest


class BaseTestAnsibleController(BaseTest):

    def setUp(self):
        super(BaseTestAnsibleController, self).setUp()

        self.test_task_result = TaskResult.objects.create()
