from django_celery_results.models import TaskResult
from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base import BaseTest


class TestCeleryTaskAPIViews(BaseTest):

    def setUp(self):
        super(TestCeleryTaskAPIViews, self).setUp()

        test_task = TaskResult.objects.create(task_id=1, status="PENDING")

        self.url = reverse('get_task_result', args=[test_task.id])

    def test_admin_can_get_task(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("id" in response.json())
        self.assertTrue("status" in response.json())
        self.assertEqual(response.data["status"], "PENDING")

    def test_cannot_get_task_when_not_admin(self):
        self.client.force_login(user=self.standard_user_2)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_get_task_when_logout(self):
        self.client.logout()
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
