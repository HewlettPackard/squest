from service_catalog.forms import FormGenerator
from service_catalog.models import TowerSurveyField
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestFormGenerator(BaseTestRequest):

    def setUp(self):
        super(TestFormGenerator, self).setUp()

    def test_apply_jinja_template_to_survey_empty_default(self):

        self.test_request.operation.job_template.survey = {
            "name": "test-survey",
            "description": "test-survey-description",
            "spec": [
                {
                    "choices": "",
                    "default": "",
                    "max": 1024,
                    "min": 0,
                    "new_question": True,
                    "question_description": "",
                    "question_name": "String variable",
                    "required": True,
                    "type": "text",
                    "variable": "text_variable"
                }
            ]
        }
        self.test_request.operation.job_template.save()

        # test with en empty string
        target_field = TowerSurveyField.objects.get(variable="text_variable", operation=self.create_operation_test)
        expected_result = ""
        target_field.default = expected_result
        target_field.save()
        form_generator = FormGenerator(user=self.standard_user, squest_request=self.test_request)
        form_generator._add_all_fields()
        self.assertEqual(expected_result, form_generator.django_form['text_variable'].initial)

    def test_apply_jinja_template_to_survey_override_default(self):
        self.test_request.operation.job_template.survey = {
            "name": "test-survey",
            "description": "test-survey-description",
            "spec": [
                {
                    "choices": "",
                    "default": "this_was_the_default",
                    "max": 1024,
                    "min": 0,
                    "new_question": True,
                    "question_description": "",
                    "question_name": "String variable",
                    "required": True,
                    "type": "text",
                    "variable": "text_variable"
                }
            ]
        }
        self.test_request.operation.job_template.save()
        # test with en empty string
        target_field = TowerSurveyField.objects.get(variable="text_variable", operation=self.create_operation_test)
        expected_result = "this_is_the_new_default"
        target_field.default = expected_result
        target_field.save()
        form_generator = FormGenerator(user=self.standard_user, squest_request=self.test_request)
        form_generator._add_all_fields()
        self.assertEqual(expected_result, form_generator.django_form['text_variable'].initial)

    def test_apply_jinja_template_to_survey_with_spec_variable(self):
        self.test_request.operation.job_template.survey = {
            "name": "test-survey",
            "description": "test-survey-description",
            "spec": [
                {
                    "choices": "",
                    "default": "this_was_the_default",
                    "max": 1024,
                    "min": 0,
                    "new_question": True,
                    "question_description": "",
                    "question_name": "String variable",
                    "required": True,
                    "type": "text",
                    "variable": "text_variable"
                }
            ]
        }
        self.job_template_test.save()
        # test with jinja string
        target_field = TowerSurveyField.objects.get(variable="text_variable", operation=self.create_operation_test)
        target_field.default = "{{ instance.spec.os }} {{ user.email }}"
        target_field.save()
        self.test_instance.spec = {
            "os": "linux"
        }
        self.test_instance.save()
        expected_result = "linux stan.1234@hpe.com"
        form_generator = FormGenerator(user=self.standard_user,
                                       squest_request=self.test_request, squest_instance=self.test_instance)
        form_generator._add_all_fields()
        self.assertEqual(expected_result, form_generator.django_form['text_variable'].initial)

    def test_get_customer_field_only(self):
        form_generator = FormGenerator(user=self.standard_user, operation=self.create_operation_test)
        form_generator._add_customer_field_only()
        self.assertCountEqual(self.create_operation_test.tower_survey_fields.filter(is_customer_field=True).values_list('variable', flat=True), form_generator.django_form.keys())
