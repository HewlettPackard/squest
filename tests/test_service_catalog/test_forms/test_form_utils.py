from django.test import override_settings

from service_catalog.forms import ServiceRequestForm
from service_catalog.forms.form_utils import FormUtils
from service_catalog.models.survey_field import SurveyField
from tests.test_service_catalog.base import BaseTest


class TestFormUtils(BaseTest):

    def setUp(self):
        super(TestFormUtils, self).setUp()
        enabled_survey_fields = {
            'text_variable': True,
            'multiplechoice_variable': False,
            'multiselect_var': False,
            'textarea_var': False,
            'password_var': False,
            'float_var': False,
            'integer_var': False
        }
        self.create_operation_test.switch_survey_fields_enable_from_dict(enabled_survey_fields)

    def test_template_field_no_default_no_spec(self):
        default_template_config = ""
        spec_config = ""
        expected_result = ""
        self.assertEqual(expected_result,
                         FormUtils.template_field(default_template_config, spec_config))

    def test_template_field_default_no_spec(self):
        default_template_config = "my_default_value"
        spec_config = ""
        expected_result = "my_default_value"
        self.assertEqual(expected_result,
                         FormUtils.template_field(default_template_config, spec_config))

    def test_template_field_default_and_valid_spec(self):
        default_template_config = "value with {{ spec.os }}"
        spec_config = {
            "spec": {
                "os": "linux"
            },
            "user_spec": {}
        }
        expected_result = "value with linux"
        self.assertEqual(expected_result,
                         FormUtils.template_field(default_template_config, spec_config))

    def test_template_field_default_and_valid_spec_and_user_spec(self):
        default_template_config = "value with {{ spec.os }} and {{ user_spec.key1 }}"
        spec_config = {
            "spec": {
                "os": "linux"
            },
            "user_spec": {
                "key1": "value1"
            }
        }
        expected_result = "value with linux and value1"
        self.assertEqual(expected_result,
                         FormUtils.template_field(default_template_config, spec_config))

    def test_template_field_default_and_valid_spec_contains_integer(self):
        default_template_config = "value with {{ spec.os }}"
        spec_config = {
            "spec": {
                "os": 12
            },
            "user_spec": {}
        }
        expected_result = "value with 12"
        self.assertEqual(expected_result,
                         FormUtils.template_field(default_template_config, spec_config))

    def test_template_field_default_and_valid_spec_list(self):
        default_template_config = "value with {{ spec.os[0] }}"
        spec_config = {
            "spec": {
                "os": ["linux", "windows"]
            },
            "user_spec": {}
        }
        expected_result = "value with linux"
        self.assertEqual(expected_result,
                         FormUtils.template_field(default_template_config, spec_config))

    def test_template_field_default_and_valid_spec_dict(self):
        default_template_config = "value with {{ spec.os['linux'] }}"
        spec_config = {
            "spec": {
                "os": {"linux": "ubuntu"}
            },
            "user_spec": {}
        }
        expected_result = "value with ubuntu"
        self.assertEqual(expected_result,
                         FormUtils.template_field(default_template_config, spec_config))

    def test_template_field_default_and_non_valid_spec_field(self):
        default_template_config = "value with {{ spec.non_exist }}"
        spec_config = {
            "spec": {
                "os": "linux"
            },
            "user_spec": {}
        }
        expected_result = "value with "
        self.assertEqual(expected_result,
                         FormUtils.template_field(default_template_config, spec_config))

    def test_template_field_none_value_as_template_data_dict(self):
        default_template_config = "default_template_config"
        self.assertEqual("default_template_config", FormUtils.template_field(default_template_config, None))

    def test_template_field_default_and_non_valid_spec_name(self):
        default_template_config = "value with {{ non_exist.my_key }}"
        spec_config = {
            "spec": {
                "other": "linux"
            },
            "user_spec": {}
        }
        expected_result = ""
        self.assertEqual(expected_result,
                         FormUtils.template_field(default_template_config, spec_config))

    def test_template_field_default_and_spec_with_filter(self):
        default_template_config = "{{ spec.multiple | join('\n') }}"
        spec_config = {
            "spec": {
                "multiple": ["value1",
                             "value2"]
            },
            "user_spec": {}
        }
        expected_result = "value1\nvalue2"
        self.assertEqual(expected_result,
                         FormUtils.template_field(default_template_config, spec_config))

    @override_settings(FIELD_VALIDATOR_PATH="tests/test_plugins/field_validators_test")
    def test_service_request_form_with_validators(self):
        target_field = SurveyField.objects.get(name="text_variable", operation=self.create_operation_test)
        target_field.validators = "even_number,superior_to_10"
        target_field.save()
        parameters = {
            'operation': self.create_operation_test,
            "quota_scope": self.test_quota_scope,
            "user": self.standard_user,
        }

        # not valid because not even number
        data = {
            "text_variable": "3"
        }
        form = ServiceRequestForm(data, **parameters)
        self.assertFalse(form.is_valid())

        # not valid because not superior to 10
        data = {
            "text_variable": "9"
        }
        form = ServiceRequestForm(data, **parameters)
        self.assertFalse(form.is_valid())

        # valid because superior to 10 and even number
        data = {
            "text_variable": "12"
        }
        form = ServiceRequestForm(data, **parameters)
        self.assertTrue(form.is_valid())
