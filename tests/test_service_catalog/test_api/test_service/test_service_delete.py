from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import Service
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestApiServiceDelete(BaseTestRequest):

    def setUp(self):
        super(TestApiServiceDelete, self).setUp()
        self.service_to_delete_id = self.service_test.id
        self.kwargs = {
            'pk': self.service_test.id
        }
        self.get_request_details_url = reverse('api_service_details', kwargs=self.kwargs)

    def test_admin_delete_request(self):
        service_count = Service.objects.count()
        response = self.client.delete(self.get_request_details_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(service_count - 1, Service.objects.count())
        self.assertFalse(Service.objects.filter(id=self.service_to_delete_id).exists())

    def test_customer_cannot_delete_request(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.delete(self.get_request_details_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_delete_request_when_logout(self):
        self.client.logout()
        response = self.client.delete(self.get_request_details_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
