from django.urls import reverse

from service_catalog.models import InstanceState
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestCustomerInstanceDetails(BaseTestRequest):

    def setUp(self):
        super(TestCustomerInstanceDetails, self).setUp()
        self.test_instance.state = InstanceState.AVAILABLE
        self.test_instance.save()
        self.args = {
            "pk": self.test_instance.id
        }

    def test_get_instance_details(self):
        url = reverse('service_catalog:instance_details', kwargs=self.args)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response.context['operations_table'])
