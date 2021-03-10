from django.core.exceptions import PermissionDenied
from django.urls import reverse

from tests.base import BaseTest


class CatalogViewTestCase(BaseTest):

    def setUp(self):
        super(CatalogViewTestCase, self).setUp()

    def test_delete_service_operation(self):
        # delete a "CREATE" type operation
        args = {
            'service_id': self.service_test.id,
            'operation_id': self.create_operation_test.id
        }
        url = reverse('delete_service_operation', kwargs=args)
        response = self.client.post(url)
        self.assertRaises(PermissionDenied)

        # delete an "UPDATE" type operation
        args = {
            'service_id': self.service_test.id,
            'operation_id': self.update_operation_test.id
        }
        url = reverse('delete_service_operation', kwargs=args)
        response = self.client.post(url)
        self.assertEquals(302, response.status_code)
