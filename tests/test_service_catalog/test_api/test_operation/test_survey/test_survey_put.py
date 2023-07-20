from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models.tower_survey_field import TowerSurveyField
from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.utils import check_data_in_dict


class TestOperationSurveyPut(BaseTestRequest):

    def setUp(self):
        super(TestOperationSurveyPut, self).setUp()
        self.kwargs = {'service_id': self.service_test.id, 'pk': self.test_request.operation.id}
        self.get_operation_survey_put_url = reverse('api_operation_survey_list_update', kwargs=self.kwargs)

    def _validate_field_in_db(self, json_data):
        for field in json_data:
            target_object = TowerSurveyField.objects.get(operation_id=self.test_request.operation.id,
                                                         name=field["name"])
            self.assertEqual(field["is_customer_field"], target_object.is_customer_field)
            self.assertEqual(field["default"], target_object.default)

    def test_admin_can_update_full_survey(self):
        data = [
            {'name': 'text_variable', 'is_customer_field': True, 'default': "text_variable_default"},
            {'name': 'multiplechoice_variable', 'is_customer_field': False, 'default': "multiplechoice_variable_default"},
            {'name': 'multiselect_var', 'is_customer_field': False, 'default': "multiselect_var_default"},
            {'name': 'textarea_var', 'is_customer_field': False, 'default': 'textarea_var_default'},
            {'name': 'password_var', 'is_customer_field': True, 'default': "password_var_default"},
            {'name': 'integer_var', 'is_customer_field': True, 'default': '1'},
            {'name': 'float_var', 'is_customer_field': True, 'default': '2'}
        ]
        response = self.client.put(self.get_operation_survey_put_url, data=data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        check_data_in_dict(self, data, response.data)
        self._validate_field_in_db(data)

    def test_admin_can_partially_update_survey(self):
        data = [
            {'name': 'text_variable', 'is_customer_field': False, 'default': "text_variable_default"},
            {'name': 'multiplechoice_variable', 'is_customer_field': True, 'default': "multiplechoice_variable_default",
             "validators": "even_number"}
        ]
        response = self.client.put(self.get_operation_survey_put_url, data=data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        check_data_in_dict(self, data, response.data)
        self._validate_field_in_db(data)

    def test_wrong_survey_field_name(self):
        data = [
            {'name': 'non_exist', 'is_customer_field': False, 'default': "test"},
        ]
        response = self.client.put(self.get_operation_survey_put_url, data=data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_wrong_survey_enable_field(self):
        data = [
            {'name': 'text_variable', 'is_customer_field': "string", 'default': "test"},
        ]
        response = self.client.put(self.get_operation_survey_put_url, data=data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
