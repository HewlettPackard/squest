from django.core.exceptions import PermissionDenied
from django.urls import reverse

from tests.test_service_catalog.base import BaseTest


class OperationDeleteTestCase(BaseTest):

    def setUp(self):
        super(OperationDeleteTestCase, self).setUp()

    def test_delete_service_operation(self):
        # delete a "CREATE" type operation
        args = {
            'service_id': self.service_test.id,
            'operation_id': self.create_operation_test.id
        }
        url = reverse('service_catalog:delete_service_operation', kwargs=args)
        response = self.client.get(url)
        self.assertEquals(403, response.status_code)
        response = self.client.post(url)
        self.assertRaises(PermissionDenied)

        # delete an "UPDATE" type operation
        args = {
            'service_id': self.service_test.id,
            'operation_id': self.update_operation_test.id
        }
        url = reverse('service_catalog:delete_service_operation', kwargs=args)
        response = self.client.get(url)
        self.assertEquals(200, response.status_code)
        response = self.client.post(url)
        self.assertEquals(302, response.status_code)
