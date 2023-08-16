from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import Service
from tests.test_service_catalog.base_test_request import BaseTestRequestAPI


class TestApiServiceList(BaseTestRequestAPI):

    def setUp(self):
        super(TestApiServiceList, self).setUp()
        self.get_service_list_url = reverse('api_service_list_create')
        self.service_test_2.enabled = False
        self.service_test_2.save()

    def test_admin_get_all_services(self):
        response = self.client.get(self.get_service_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], Service.objects.count())

    def test_customer_get_services(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.get_service_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], Service.objects.count())

    def test_cannot_get_service_list_when_logout(self):
        self.client.logout()
        response = self.client.get(self.get_service_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
