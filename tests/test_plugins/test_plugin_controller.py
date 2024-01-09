from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from rest_framework import serializers
from Squest.utils.plugin_controller import PluginController


class TestPluginController(TestCase):
    ######################################################
    # Field validators
    ######################################################
    @override_settings(FIELD_VALIDATOR_PATH="tests/test_plugins/field_validators_test")
    def test_get_user_provisioned_field_validators(self):
        expected_list = [
            "even_number",
            "superior_to_10"
        ]
        self.assertEqual(expected_list, PluginController.get_user_provisioned_field_validators())

    @override_settings(FIELD_VALIDATOR_PATH="tests/test_plugins/field_validators_test")
    def test_get_ui_field_validator_def(self):
        loaded_module = PluginController.get_ui_field_validator_def("even_number")
        with self.assertRaises(ValidationError):
            loaded_module(3)
        loaded_module = PluginController.get_ui_field_validator_def("superior_to_10")
        with self.assertRaises(ValidationError):
            loaded_module(3)

    @override_settings(FIELD_VALIDATOR_PATH="tests/test_plugins/field_validators_test")
    def test_get_api_field_validator_def(self):
        loaded_module = PluginController.get_api_field_validator_def("even_number")
        with self.assertRaises(serializers.ValidationError):
            loaded_module(3)
        loaded_module = PluginController.get_api_field_validator_def("superior_to_10")
        with self.assertRaises(serializers.ValidationError):
            loaded_module(3)

    @override_settings(FIELD_VALIDATOR_PATH="tests/test_plugins/field_validators_test")
    def test_get_ui_field_validator_def_return_none_if_wrong_file(self):
        self.assertIsNone(PluginController.get_api_field_validator_def("does_not_exist"))

    ######################################################
    # Survey validators
    ######################################################
    @override_settings(SURVEY_VALIDATOR_PATH="tests/test_plugins/survey_validators_test")
    def test_get_user_provisioned_survey_validators(self):
        expected_list = [
            'survey_test.Validator1',
            'survey_test.Validator2',
            'survey_test.ValidatorDay1',
            'survey_test.ValidatorDay2'
        ]

        self.assertCountEqual(expected_list, PluginController.get_user_provisioned_survey_validators())

    @override_settings(SURVEY_VALIDATOR_PATH="tests/test_plugins/survey_validators_test")
    def test_get_survey_validator_def(self):
        survey_validator = PluginController.get_survey_validator_def("survey_test.Validator1")
        with self.assertRaises(serializers.ValidationError):
            survey_validator(survey={'vcpu': 0, 'ram': 0}, user=1, operation=2, instance=3)._validate()

        survey_validator(survey={}, user=1, operation=2, instance=3)._validate()

    @override_settings(SURVEY_VALIDATOR_PATH="tests/test_plugins/survey_validators_test")
    def test_get_survey_validator_def_return_none_if_wrong_file(self):
        self.assertIsNone(PluginController.get_survey_validator_def("does_not_exist"))
