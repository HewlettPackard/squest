from guardian.mixins import UserObjectPermission

from service_catalog.forms import AcceptRequestForm
from service_catalog.models import Request, Instance
from tests.base import BaseTest


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
        expected_result = "User"
        self.assertEquals(expected_result, AcceptRequestForm._get_field_group(field_name, enabled_field))

        field_name = 'multiplechoice_variable'
        expected_result = "Admin"
        self.assertEquals(expected_result, AcceptRequestForm._get_field_group(field_name, enabled_field))

    def test_accept_forms_field_count(self):
        parameters = {
            'request_id': self.test_request.id
        }
        data = {'multiselect_var': ['multiselect_2', 'multiselect_3'],
                'text_var': ['text_val'],
                'textarea_var': ['text_area'],
                'password_var': ['aa'],
                'choice_var': ['choice_2'],
                'integer_var': ['1'],
                'float_var': ['1.5']}
        form = AcceptRequestForm(self.superuser, data, **parameters)
        self.assertEquals(len(self.test_request.fill_in_survey), len(form.fields))
