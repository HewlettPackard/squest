from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import Request, InstanceState
from tests.test_service_catalog.base_test_request import BaseTestRequestAPI


class TestApiOperationRequestCreate(BaseTestRequestAPI):

    def setUp(self):
        super(TestApiOperationRequestCreate, self).setUp()
        self.test_instance.state = InstanceState.AVAILABLE
        self.test_instance.save()
        self.kwargs = {
            "instance_id": self.test_instance.id,
            "operation_id": self.update_operation_test.id,
        }
        self.url = reverse('api_operation_request_create', kwargs=self.kwargs)
        self.data = {
            'fill_in_survey': {
                'text_variable': 'my text'
            }
        }
        self.expected = {'text_variable': 'my text', 'request_comment': None}

    def test_can_create(self):
        request_count = Request.objects.count()
        response = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(request_count + 1, Request.objects.count())
        self.assertIn('id', response.data.keys())
        self.assertTrue(isinstance(response.data['fill_in_survey'], dict))
        self.assertEqual(response.data['fill_in_survey'], self.expected)

    def test_cannot_create_with_disabled_operation(self):
        self.update_operation_test.enabled = False
        self.update_operation_test.save()
        request_count = Request.objects.count()
        response = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(request_count, Request.objects.count())

    def test_customer_cannot_create_an_admin_operation(self):
        self.client.force_login(self.standard_user)
        self.update_operation_test.permission = self.admin_operation
        self.update_operation_test.save()
        request_count = Request.objects.count()
        response = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(request_count, Request.objects.count())

    def test_cannot_create_on_provisioning_operation(self):
        self.kwargs = {
            "instance_id": self.test_instance.id,
            "operation_id": self.create_operation_test.id,
        }
        self.url = reverse('api_operation_request_create', kwargs=self.kwargs)
        request_count = Request.objects.count()
        response = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(request_count, Request.objects.count())

    def test_cannot_create_on_non_own_instance(self):
        self.client.force_login(self.standard_user_2)
        request_count = Request.objects.count()
        response = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(request_count, Request.objects.count())

    def test_cannot_create_when_logout(self):
        self.client.logout()
        response = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_create_on_non_existing_instance(self):
        self.kwargs['instance_id'] = 9999999
        self.url = reverse('api_operation_request_create', kwargs=self.kwargs)
        response = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_create_on_non_existing_operation(self):
        self.kwargs['operation_id'] = 9999999
        self.url = reverse('api_operation_request_create', kwargs=self.kwargs)
        response = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_create_with_wrong_survey_fields(self):
        self.data['fill_in_survey']['wrong_field_name'] = self.data['fill_in_survey'].pop('text_variable')
        response = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
