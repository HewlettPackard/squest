from django.urls import reverse

from service_catalog.models import Request
from service_catalog.models.instance import InstanceState
from tests.base_test_request import BaseTestRequest


class TestCustomerInstanceRequestOperation(BaseTestRequest):

    def setUp(self):
        super(TestCustomerInstanceRequestOperation, self).setUp()
        self.test_instance.state = InstanceState.AVAILABLE
        self.test_instance.save()

    def test_can_create_operation_request(self):
        # get number of request before submitting
        current_request_number = Request.objects.all().count()
        expected_request_number = current_request_number + 1
        args = {
            'instance_id': self.test_instance.id,
            'operation_id': self.update_operation_test.id
        }
        data = {'text_variable': 'my_var'}
        url = reverse('service_catalog:customer_instance_request_new_operation', kwargs=args)
        response = self.client.post(url, data=data)
        self.assertEquals(302, response.status_code)
        self.test_instance.refresh_from_db()
        self.assertEquals(self.test_instance.state, InstanceState.AVAILABLE)
        self.assertEquals(expected_request_number, Request.objects.all().count())

    def test_cannot_request_non_valid_operation(self):
        # operation belong to another service
        args = {
            'instance_id': self.test_instance.id,
            'operation_id': self.update_operation_test_2.id
        }
        data = {'text_variable': 'my_var'}
        url = reverse('service_catalog:customer_instance_request_new_operation', kwargs=args)
        response = self.client.post(url, data=data)
        self.assertEquals(403, response.status_code)

    def test_cannot_request_non_available_instance(self):
        for state in [InstanceState.PENDING, InstanceState.PROVISIONING, InstanceState.DELETING, InstanceState.DELETED]:
            self.test_instance.state = state
            self.test_instance.save()
            args = {
                'instance_id': self.test_instance.id,
                'operation_id': self.update_operation_test.id
            }
            data = {'text_variable': 'my_var'}
            url = reverse('service_catalog:customer_instance_request_new_operation', kwargs=args)
            response = self.client.post(url, data=data)
            self.assertEquals(403, response.status_code)
