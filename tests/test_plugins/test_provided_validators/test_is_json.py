from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from rest_framework import serializers
from Squest.utils.plugin_controller import PluginController


class TestSSHPublicKeyValidator(TestCase):
    def test_with_text(self):
        json_text = "aaaabbbbcccc"
        loaded_module = PluginController.get_ui_field_validator_def("is_json")
        with self.assertRaises(ValidationError):
            loaded_module(json_text)
        loaded_module = PluginController.get_api_field_validator_def("is_json")
        with self.assertRaises(serializers.ValidationError):
            loaded_module(json_text)

    def test_with_empty_text(self):
        json_text = ""
        loaded_module = PluginController.get_ui_field_validator_def("is_json")
        with self.assertRaises(ValidationError):
            loaded_module(json_text)
        loaded_module = PluginController.get_api_field_validator_def("is_json")
        with self.assertRaises(serializers.ValidationError):
            loaded_module(json_text)

    def test_with_double_json(self):
        json_text = '{"my_json": "is_ok", other_json: {"in_side": 13}}{"outside": "is_not_ok"}'
        loaded_module = PluginController.get_ui_field_validator_def("is_json")
        with self.assertRaises(ValidationError):
            loaded_module(json_text)
        loaded_module = PluginController.get_api_field_validator_def("is_json")
        with self.assertRaises(serializers.ValidationError):
            loaded_module(json_text)

    def test_with_single_quote(self):
        json_text = "{'my_json': 'is_ok', other_json: {'in_side': 13}}"
        loaded_module = PluginController.get_ui_field_validator_def("is_json")
        with self.assertRaises(ValidationError):
            loaded_module(json_text)
        loaded_module = PluginController.get_api_field_validator_def("is_json")
        with self.assertRaises(serializers.ValidationError):
            loaded_module(json_text)

    def test_with_missing_quote(self):
        json_text = '{"my_json": "is_ok", other_json: {"in_side": 13}}'
        loaded_module = PluginController.get_ui_field_validator_def("is_json")
        with self.assertRaises(ValidationError):
            loaded_module(json_text)
        loaded_module = PluginController.get_api_field_validator_def("is_json")
        with self.assertRaises(serializers.ValidationError):
            loaded_module(json_text)

    def test_with_additional_comma(self):
        json_text = '{"my_json": "is_ok", "other_json": {"in_side": 13},}'
        loaded_module = PluginController.get_ui_field_validator_def("is_json")
        with self.assertRaises(ValidationError):
            loaded_module(json_text)
        loaded_module = PluginController.get_api_field_validator_def("is_json")
        with self.assertRaises(serializers.ValidationError):
            loaded_module(json_text)

    def test_with_json(self):
        json_text = '{"my_json": "is_ok", "other_json": {"in_side": 13}}'
        loaded_module = PluginController.get_api_field_validator_def("is_json")
        try:
            loaded_module(json_text)
        except ValidationError:
            self.fail("UI validator fail")
        loaded_module = PluginController.get_api_field_validator_def("is_json")
        try:
            loaded_module(json_text)
        except serializers.ValidationError:
            self.fail("API validator fail")
