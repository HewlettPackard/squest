from service_catalog.forms.tower_survey_field_form import TowerSurveyFieldForm
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestTowerSurveyFieldForm(BaseTestRequest):

    def setUp(self):
        super().setUp()
        self.data = {
            'is_customer_field': True,
            'default': 'multiplechoice_variable_default',
            'validators': [],
            'attribute_definition': self.cpu_attribute.id
        }

    def test_set_attribute_on_integer_field(self):
        field = self.create_operation_test.tower_survey_fields.filter(type="integer").first()
        form = TowerSurveyFieldForm(instance=field, data=self.data)
        self.assertTrue(form.is_valid())

    def test_cannot_set_attribute_on_float_field(self):
        field = self.create_operation_test.tower_survey_fields.filter(type="float").first()
        form = TowerSurveyFieldForm(instance=field, data=self.data)
        self.assertFalse(form.is_valid())

    def test_cannot_set_attribute_on_multiselect_field(self):
        field = self.create_operation_test.tower_survey_fields.filter(type="multiselect").first()
        form = TowerSurveyFieldForm(instance=field, data=self.data)
        self.assertFalse(form.is_valid())

    def test_cannot_set_attribute_on_multiplechoice_field(self):
        field = self.create_operation_test.tower_survey_fields.filter(type="multiplechoice").first()
        form = TowerSurveyFieldForm(instance=field, data=self.data)
        self.assertFalse(form.is_valid())

    def test_cannot_set_attribute_on_password_field(self):
        field = self.create_operation_test.tower_survey_fields.filter(type="password").first()
        form = TowerSurveyFieldForm(instance=field, data=self.data)
        self.assertFalse(form.is_valid())

    def test_cannot_set_attribute_on_textarea_field(self):
        field = self.create_operation_test.tower_survey_fields.filter(type="textarea").first()
        form = TowerSurveyFieldForm(instance=field, data=self.data)
        self.assertFalse(form.is_valid())

    def test_cannot_set_attribute_on_text_field(self):
        field = self.create_operation_test.tower_survey_fields.filter(type="text").first()
        form = TowerSurveyFieldForm(instance=field, data=self.data)
        self.assertFalse(form.is_valid())
