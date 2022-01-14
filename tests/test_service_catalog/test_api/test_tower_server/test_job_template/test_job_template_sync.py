from unittest import mock

from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base import BaseTest


class TestApiJobTemplateSyncAll(BaseTest):

    def setUp(self):
        super(TestApiJobTemplateSyncAll, self).setUp()

    def setup_sync_all_test(self):
        self.kwargs = {
            'tower_server_id': self.tower_server_test.id,
        }
        self.url = reverse('api_job_template_sync_all', kwargs=self.kwargs)

    def setup_sync_single_job_template_test(self):
        self.kwargs = {
            'tower_server_id': self.tower_server_test.id,
            'job_template_id': self.job_template_test.id
        }
        self.url = reverse('api_job_template_sync', kwargs=self.kwargs)

    def _check_can_sync_job_template(self, expected_argument):
        with mock.patch("service_catalog.models.tower_server.TowerServer.sync") as mock_sync:
            response = self.client.post(self.url, format='json')
            self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
            self.assertTrue("id" in response.json())
            self.assertTrue("status" in response.json())
            self.assertEqual(response.data["status"], "PENDING")
            mock_sync.assert_called_with(*expected_argument)

    def _check_cannot_sync_when_not_admin(self):
        self.client.force_login(user=self.standard_user_2)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _check_cannot_sync_when_logout(self):
        self.client.logout()
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_sync_all(self):
        self.setup_sync_all_test()
        self._check_can_sync_job_template(expected_argument=[None])

    def test_cannot_sync_all_when_not_admin(self):
        self.setup_sync_all_test()
        self._check_cannot_sync_when_not_admin()

    def test_cannot_sync_all_when_logout(self):
        self.setup_sync_all_test()
        self._check_cannot_sync_when_logout()

    def test_admin_can_sync_single_job_template(self):
        self.setup_sync_single_job_template_test()
        self._check_can_sync_job_template(expected_argument=[self.job_template_test.id])

    def test_cannot_sync_single_job_template_when_not_admin(self):
        self.setup_sync_single_job_template_test()
        self._check_cannot_sync_when_not_admin()

    def test_cannot_sync_single_job_template_when_logout(self):
        self.setup_sync_single_job_template_test()
        self._check_cannot_sync_when_logout()
