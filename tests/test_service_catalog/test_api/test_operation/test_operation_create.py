from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import OperationType
from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.utils import check_data_in_dict


class TestApiOperationCreate(BaseTestRequest):

    def setUp(self):
        super(TestApiOperationCreate, self).setUp()
        self.kwargs = {'service_id': self.service_test.id}
        self.post_data = {
            'name': "My new name",
            'description': "My new description",
            'type': OperationType.UPDATE,
            'enabled_survey_fields': {
                'float_var': True,
                'integer_var': True,
                'multiplechoice_variable': True,
                'multiselect_var': True,
                'password_var': True,
                'text_variable': True,
                'textarea_var': True
            },
            'auto_accept': False,
            'auto_process': False,
            'process_timeout_second': 60,
            'job_template': self.job_template_test.id
        }
        self.get_operation_details_url = reverse('api_operation_list_create', kwargs=self.kwargs)

    def test_admin_post_operation(self):
        response = self.client.post(self.get_operation_details_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        check_data_in_dict(self, [self.post_data], [response.data])

    def test_service_cannot_have_several_create_operation(self):
        self.post_data['type'] = OperationType.CREATE
        response = self.client.post(self.get_operation_details_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.service_test.operations.filter(type=OperationType.CREATE).count(), 1)

    def test_admin_cannot_post_on_operation_not_full(self):
        self.post_data.pop('name')
        response = self.client.post(self.get_operation_details_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_customer_cannot_post_operation(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.post(self.get_operation_details_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_post_operation_when_loggout(self):
        self.client.logout()
        response = self.client.post(self.get_operation_details_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def check_data_in_dict(self, expected_data_list, data_list):
        for expected_data, data in zip(expected_data_list, data_list):
            for key_var, val_var in expected_data.items():
                self.assertIn(key_var, data.keys())
                self.assertEqual(val_var, data[key_var])
