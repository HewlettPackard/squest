from service_catalog.forms import AcceptRequestForm
from service_catalog.forms.utils import _get_field_group
from service_catalog.models import Request, Instance
from tests.test_service_catalog.base import BaseTest


class TestServiceRequestForm(BaseTest):

    def setUp(self):
        super(TestServiceRequestForm, self).setUp()
        data = {
            'text_variable': 'my_var',
            'multiplechoice_variable': 'choice1', 'multiselect_var': 'multiselect_1',
            'textarea_var': '2',
            'password_var': 'pass',
            'integer_var': '1',
            'float_var': '0.6'
        }
        self.test_instance = Instance.objects.create(name="test_instance_1", service=self.service_test,
                                                     spoc=self.standard_user)
        # add a first request
        self.test_request = Request.objects.create(fill_in_survey=data,
                                                   instance=self.test_instance,
                                                   operation=self.create_operation_test,
                                                   user=self.standard_user)

    def test_get_field_group(self):
        # test 1 - one field is admin
        field_name = 'text_variable'
        enabled_field = {
            'text_variable': True,
            'multiplechoice_variable': False,
            'multiselect_var': False,
            'textarea_var': False,
            'password_var': False,
            'float_var': False,
            'integer_var': False
        }
        self.create_operation_test.switch_tower_fields_enable_from_dict(enabled_field)
        expected_result = "3. User fields"
        self.assertEqual(expected_result, _get_field_group(field_name,
                                                           self.test_request.operation.tower_survey_fields.all()))
        field_name = 'multiplechoice_variable'
        expected_result = "2. Admin fields"
        self.assertEqual(expected_result, _get_field_group(field_name,
                                                           self.test_request.operation.tower_survey_fields.all()))
        # test 2 - all field for admin
        enabled_field = {
            'text_variable': False,
            'multiplechoice_variable': False,
            'multiselect_var': False,
            'textarea_var': False,
            'password_var': False,
            'float_var': False,
            'integer_var': False
        }
        self.create_operation_test.switch_tower_fields_enable_from_dict(enabled_field)
        expected_result = "2. Admin fields"
        self.assertEqual(expected_result, _get_field_group(field_name, self.test_request.operation.tower_survey_fields.all()))

        # test 3 - all field user
        enabled_field = {
            'text_variable': True,
            'multiplechoice_variable': True,
            'multiselect_var': True,
            'textarea_var': True,
            'password_var': True,
            'float_var': True,
            'integer_var': True
        }
        self.create_operation_test.switch_tower_fields_enable_from_dict(enabled_field)
        expected_result = "2. User fields"
        self.assertEqual(expected_result,
                         _get_field_group(field_name, self.test_request.operation.tower_survey_fields.all()))

    def test_accept_forms_field_count(self):
        parameters = {
            'request': self.test_request
        }
        data = {
            'squest_instance_name': self.test_request.instance.name,
            'billing_group_id': self.test_request.instance.billing_group_id,
            'multiselect_var': ['multiselect_2', 'multiselect_3'],
            'text_var': ['text_val'],
            'textarea_var': ['text_area'],
            'password_var': ['aa'],
            'choice_var': ['choice_2'],
            'integer_var': ['1'],
            'float_var': ['1.5']
        }
        form = AcceptRequestForm(self.superuser, data, **parameters)
        self.assertEqual(len(self.test_request.fill_in_survey), len(form.fields) - 2)
