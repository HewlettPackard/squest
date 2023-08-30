from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import JobTemplate
from tests.test_service_catalog.base_test_request import BaseTestRequestAPI


class TestApiTowerServerList(BaseTestRequestAPI):

    def setUp(self):
        super(TestApiTowerServerList, self).setUp()
        self.tower_server_url = f"{reverse('api_jobtemplate_list')}?tower_server={self.tower_server_test.id}"

    def test_admin_get_job_template_of_tower_server(self):
        response = self.client.get(self.tower_server_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], JobTemplate.objects.filter(tower_server=self.tower_server_test).count())

    def test_customer_cannot_get_job_template_of_tower_server(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.tower_server_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_get_job_template_of_tower_server_list_when_logout(self):
        self.client.logout()
        response = self.client.get(self.tower_server_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
