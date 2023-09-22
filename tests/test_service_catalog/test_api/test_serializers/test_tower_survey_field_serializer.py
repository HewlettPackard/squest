from service_catalog.api.serializers.tower_survey_field_serializer import TowerSurveyFieldSerializer

from tests.test_service_catalog.base_test_request import BaseTestRequestAPI


class TestTowerSurveyFieldSerializer(BaseTestRequestAPI):

    def setUp(self):
        super(TestTowerSurveyFieldSerializer, self).setUp()
        self.data = {
            'is_customer_field': True,
            'default': 'multiplechoice_variable_default',
            'validators': 'even_number',
            'attribute_definition': self.cpu_attribute.id
        }

    def test_set_attribute_on_integer_field(self):
        field = self.create_operation_test.tower_survey_fields.filter(type="integer").first()
        serializer = TowerSurveyFieldSerializer(instance=field, data=self.data)
        self.assertTrue(serializer.is_valid())

    def test_cannot_set_attribute_on_float_field(self):
        field = self.create_operation_test.tower_survey_fields.filter(type="float").first()
        serializer = TowerSurveyFieldSerializer(instance=field, data=self.data)
        self.assertFalse(serializer.is_valid())

    def test_cannot_set_attribute_on_multiselect_field(self):
        field = self.create_operation_test.tower_survey_fields.filter(type="multiselect").first()
        serializer = TowerSurveyFieldSerializer(instance=field, data=self.data)
        self.assertFalse(serializer.is_valid())

    def test_cannot_set_attribute_on_multiplechoice_field(self):
        field = self.create_operation_test.tower_survey_fields.filter(type="multiplechoice").first()
        serializer = TowerSurveyFieldSerializer(instance=field, data=self.data)
        self.assertFalse(serializer.is_valid())

    def test_cannot_set_attribute_on_password_field(self):
        field = self.create_operation_test.tower_survey_fields.filter(type="password").first()
        serializer = TowerSurveyFieldSerializer(instance=field, data=self.data)
        self.assertFalse(serializer.is_valid())

    def test_cannot_set_attribute_on_textarea_field(self):
        field = self.create_operation_test.tower_survey_fields.filter(type="textarea").first()
        serializer = TowerSurveyFieldSerializer(instance=field, data=self.data)
        self.assertFalse(serializer.is_valid())

    def test_cannot_set_attribute_on_text_field(self):
        field = self.create_operation_test.tower_survey_fields.filter(type="text").first()
        serializer = TowerSurveyFieldSerializer(instance=field, data=self.data)
        self.assertFalse(serializer.is_valid())
