from service_catalog.api.serializers import AcceptRequestSerializer
from service_catalog.models import RequestState
from service_catalog.models.tower_survey_field import TowerSurveyField
from tests.test_service_catalog.base_test_request import BaseTestRequest
from django.test import override_settings


class TestAcceptRequestSerializer(BaseTestRequest):

    def setUp(self):
        super(TestAcceptRequestSerializer, self).setUp()
        self.test_request.state = RequestState.SUBMITTED
        self.test_request.save()
        self.data = {
                'text_variable': "test text var",
                'multiplechoice_variable': "choice2",
                'multiselect_var': ["multiselect_3", "multiselect_1"],
                'textarea_var': "test text area var",
                'password_var': "test_password",
                'float_var': 1.2,
                'integer_var': 6
            }

    def test_multiplechoice_field_wrong_format(self):
        self.data["multiplechoice_variable"] = 4
        serializer = AcceptRequestSerializer(data=self.data, squest_request=self.test_request, user=self.superuser)
        self.assertFalse(serializer.is_valid())

    def test_multiselect_field_wrong_format(self):
        self.data["multiselect_var"] = 4
        serializer = AcceptRequestSerializer(data=self.data, squest_request=self.test_request, user=self.superuser)
        self.assertFalse(serializer.is_valid())

    def test_password_field_too_short(self):
        self.data["password_var"] = 4
        serializer = AcceptRequestSerializer(data=self.data, squest_request=self.test_request, user=self.superuser)
        self.assertFalse(serializer.is_valid())

    def test_float_field_wrong_format(self):
        self.data["float_var"] = "toto"
        serializer = AcceptRequestSerializer(data=self.data, squest_request=self.test_request, user=self.superuser)
        self.assertFalse(serializer.is_valid())

    def test_integer_field_wrong_format(self):
        self.data["integer_var"] = 4.5
        serializer = AcceptRequestSerializer(data=self.data, squest_request=self.test_request, user=self.superuser)
        self.assertFalse(serializer.is_valid())

    @override_settings(FIELD_VALIDATOR_PATH="tests/test_plugins/field_validators_test")
    def test_field_validators(self):
        target_field = TowerSurveyField.objects.get(name="text_variable", operation=self.create_operation_test)
        target_field.validators = "even_number,superior_to_10"
        target_field.save()

        self.data["text_variable"] = "9"
        serializer = AcceptRequestSerializer(data=self.data, squest_request=self.test_request, user=self.superuser)
        self.assertFalse(serializer.is_valid())

        self.data["text_variable"] = "13"
        serializer = AcceptRequestSerializer(data=self.data, squest_request=self.test_request, user=self.superuser)
        self.assertFalse(serializer.is_valid())

        self.data["text_variable"] = "12"
        serializer = AcceptRequestSerializer(data=self.data, squest_request=self.test_request, user=self.superuser)
        self.assertTrue(serializer.is_valid())
