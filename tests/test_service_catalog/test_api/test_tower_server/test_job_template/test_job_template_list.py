from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import JobTemplate
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestApiAnsibleControllerList(BaseTestRequest):

    def setUp(self):
        super(TestApiAnsibleControllerList, self).setUp()
        self.kwargs = {
            'ansible_controller_id': self.ansible_controller_test.id
        }
        self.ansible_controller_url = reverse('api_job_template_list', kwargs=self.kwargs)

    def test_admin_get_job_template_of_ansible_controller(self):
        response = self.client.get(self.ansible_controller_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], JobTemplate.objects.filter(ansible_controller=self.ansible_controller_test).count())

    def test_customer_cannot_get_job_template_of_ansible_controller(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.ansible_controller_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_get_job_template_of_ansible_controller_list_when_logout(self):
        self.client.logout()
        response = self.client.get(self.ansible_controller_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
