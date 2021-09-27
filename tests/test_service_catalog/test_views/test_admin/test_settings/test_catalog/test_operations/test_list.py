from django.urls import reverse

from service_catalog.models import OperationType
from tests.test_service_catalog.base import BaseTest


class OperationListTestCase(BaseTest):

    def setUp(self):
        super(OperationListTestCase, self).setUp()
        args = {
            'service_id': self.service_test.id,
        }
        self.url = reverse('service_catalog:service_operations', kwargs=args)

    def test_get_operation_list(self):
        response = self.client.get(self.url)
        self.assertEquals(200, response.status_code)

    def test_customer_can_get_operation_list(self):
        self.client.logout()
        self.client.login(username=self.standard_user.username, password=self.common_password)
        response = self.client.get(self.url)
        self.assertEquals(200, response.status_code)

    def test_cannot_get_operation_list_logout(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEquals(302, response.status_code)
