from django.urls import reverse

from tests.test_service_catalog.base import BaseTest


class OperationDeleteTestCase(BaseTest):

    def setUp(self):
        super(OperationDeleteTestCase, self).setUp()

    def test_delete_service_operation(self):
        # delete a "CREATE" type operation
        args = {
            'pk': self.create_operation_test.id
        }
        url = reverse('service_catalog:operation_delete', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        response = self.client.post(url)
        self.assertEqual(302, response.status_code)
        self.service_test.refresh_from_db()
        self.assertEqual(self.service_test.enabled, False)

        # delete an "UPDATE" type operation
        args = {
            'pk': self.update_operation_test.id
        }
        url = reverse('service_catalog:operation_delete', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        response = self.client.post(url)
        self.assertEqual(302, response.status_code)
