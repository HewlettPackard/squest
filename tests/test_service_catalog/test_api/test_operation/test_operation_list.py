from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequestAPI


class TestApiOperationList(BaseTestRequestAPI):

    def setUp(self):
        super(TestApiOperationList, self).setUp()
        self.get_operation_list_url = reverse('api_operation_list_create')

    def test_get_all_operations_of_the_service(self):
        response = self.client.get(f"{self.get_operation_list_url}?service={self.service_test.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], self.service_test.operations.count())
        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.get_operation_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_get_operation_list_when_logout(self):
        self.client.logout()
        response = self.client.get(self.get_operation_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
