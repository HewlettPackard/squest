from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import Operation
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestApiOperationDelete(BaseTestRequest):

    def setUp(self):
        super(TestApiOperationDelete, self).setUp()
        self.operation_to_delete_id = self.update_operation_test.id
        self.kwargs = {
            'service_id': self.service_test.id,
            'pk': self.update_operation_test.id
        }
        self.get_operation_details_url = reverse('api_operation_details', kwargs=self.kwargs)

    def test_admin_delete_operation(self):
        operation_count = Operation.objects.count()
        response = self.client.delete(self.get_operation_details_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(operation_count - 1, Operation.objects.count())
        self.assertFalse(Operation.objects.filter(id=self.operation_to_delete_id).exists())

    def test_admin_cannot_delete_create_operation(self):
        operation_count = Operation.objects.count()
        self.kwargs = {
            'service_id': self.service_test.id,
            'pk': self.create_operation_test.id
        }
        self.get_operation_details_url = reverse('api_operation_details', kwargs=self.kwargs)
        response = self.client.delete(self.get_operation_details_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(operation_count, Operation.objects.count())
        self.assertTrue(Operation.objects.filter(id=self.create_operation_test.id).exists())

    def test_customer_cannot_delete_operation(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.delete(self.get_operation_details_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_delete_operation_when_loggout(self):
        self.client.logout()
        response = self.client.delete(self.get_operation_details_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
