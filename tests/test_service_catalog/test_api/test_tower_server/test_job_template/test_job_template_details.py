from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequestAPI


class TestApiJobTemplateDetails(BaseTestRequestAPI):

    def setUp(self):
        super(TestApiJobTemplateDetails, self).setUp()
        self.kwargs = {
            'tower_server_id': self.tower_server_test.id,
            'pk': self.job_template_test.id,
        }
        self.url = reverse('api_jobtemplate_details', kwargs=self.kwargs)

    def _assert_can_get_details(self, response):
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_keys = ['id', 'name', 'tower_id', 'survey', 'tower_job_template_data', 'is_compliant', 'tower_server']
        for key in expected_keys:
            self.assertTrue(key in response.json())

    def test_can_get_job_template_details(self):
        response = self.client.get(self.url, format='json')
        self._assert_can_get_details(response)

    def test_get_details_wrong_tower_server_id(self):
        self.kwargs = {
            'tower_server_id': self.tower_server_test_2.id,
            'pk': self.job_template_test.id,
        }
        self.url = reverse('api_jobtemplate_details', kwargs=self.kwargs)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_details_wrong_job_template_id(self):
        self.kwargs = {
            'tower_server_id': self.tower_server_test.id,
            'pk': 9999,
        }
        self.url = reverse('api_jobtemplate_details', kwargs=self.kwargs)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_customer_cannot_get_job_template_details(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_get_job_template_details_when_logout(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
