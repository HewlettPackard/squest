from django.urls import reverse

from service_catalog.models import Request, RequestMessage
from service_catalog.models.instance import InstanceState
from tests.test_service_catalog.base_test_request import BaseTestRequest


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
        url = reverse('service_catalog:instance_request_new_operation', kwargs=args)
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.test_instance.refresh_from_db()
        self.assertEqual(self.test_instance.state, InstanceState.AVAILABLE)
        self.assertEqual(expected_request_number, Request.objects.all().count())

    def test_cannot_request_disabled_operation(self):
        current_request_number = Request.objects.all().count()
        args = {
            'instance_id': self.test_instance.id,
            'operation_id': self.update_operation_test.id
        }
        self.update_operation_test.enabled = False
        self.update_operation_test.save()
        data = {'text_variable': 'my_var'}
        url = reverse('service_catalog:instance_request_new_operation', kwargs=args)
        response = self.client.post(url, data=data)
        self.assertEqual(403, response.status_code)
        self.assertEqual(current_request_number, Request.objects.all().count())

    def test_cannot_request_non_valid_operation(self):
        # operation belong to another service
        args = {
            'instance_id': self.test_instance.id,
            'operation_id': self.update_operation_test_2.id
        }
        data = {'text_variable': 'my_var'}
        url = reverse('service_catalog:instance_request_new_operation', kwargs=args)
        response = self.client.post(url, data=data)
        self.assertEqual(403, response.status_code)

    def test_cannot_request_non_available_instance(self):
        for state in [InstanceState.PENDING, InstanceState.PROVISIONING, InstanceState.DELETING, InstanceState.DELETED]:
            self.test_instance.state = state
            self.test_instance.save()
            args = {
                'instance_id': self.test_instance.id,
                'operation_id': self.update_operation_test.id
            }
            data = {'text_variable': 'my_var'}
            url = reverse('service_catalog:instance_request_new_operation', kwargs=args)
            response = self.client.post(url, data=data)
            self.assertEqual(403, response.status_code)

    def test_create_request_with_a_comment(self):
        args = {
            'instance_id': self.test_instance.id,
            'operation_id': self.update_operation_test.id
        }
        url = reverse('service_catalog:instance_request_new_operation', kwargs=args)

        data = {
            "text_variable": "this is a new text",
            "request_comment": "here_is_a_comment"
        }
        number_request_before = Request.objects.all().count()
        number_comment_before = RequestMessage.objects.all().count()
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(number_request_before + 1, Request.objects.all().count())
        self.assertEqual(number_comment_before + 1, RequestMessage.objects.all().count())

        created_request = Request.objects.latest('id')
        self.assertEqual(created_request.comments.count(), 1)
        self.assertEqual(created_request.comments.first().content, "here_is_a_comment")
        self.assertEqual(created_request.comments.first().sender, self.superuser)
