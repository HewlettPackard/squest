from service_catalog.api.serializers import AcceptRequestSerializer
from service_catalog.models import RequestState
from tests.test_service_catalog.base_test_request import BaseTestRequest


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
        serializer = AcceptRequestSerializer(data=self.data, target_request=self.test_request, user=self.superuser,
                                             read_only_form=False)
        self.assertFalse(serializer.is_valid())

    def test_multiselect_field_wrong_format(self):
        self.data["multiselect_var"] = 4
        serializer = AcceptRequestSerializer(data=self.data, target_request=self.test_request, user=self.superuser,
                                             read_only_form=False)
        self.assertFalse(serializer.is_valid())

    def test_password_field_too_short(self):
        self.data["password_var"] = 4
        serializer = AcceptRequestSerializer(data=self.data, target_request=self.test_request, user=self.superuser,
                                             read_only_form=False)
        self.assertFalse(serializer.is_valid())

    def test_float_field_wrong_format(self):
        self.data["float_var"] = "toto"
        serializer = AcceptRequestSerializer(data=self.data, target_request=self.test_request, user=self.superuser,
                                             read_only_form=False)
        self.assertFalse(serializer.is_valid())

    def test_integer_field_wrong_format(self):
        self.data["integer_var"] = 4.5
        serializer = AcceptRequestSerializer(data=self.data, target_request=self.test_request, user=self.superuser,
                                             read_only_form=False)
        self.assertFalse(serializer.is_valid())
