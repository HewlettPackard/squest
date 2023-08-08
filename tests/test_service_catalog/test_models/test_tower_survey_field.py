from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestSurveyField(BaseTestRequest):

    def test_fill_in_survey_updated(self):
        admin_fill_in_survey = {
            'multiplechoice_variable': "choice1",
            'multiselect_var': [],
            'textarea_var': "textarea_value",
            'password_var': "password_val",
            'float_var': 0,
            'integer_var': 12
        }
        fill_in_survey = {
            'text_variable': "value"
        }

        self.test_request.fill_in_survey = fill_in_survey
        self.test_request.admin_fill_in_survey = admin_fill_in_survey
        self.test_request.save()

        expected_admin_fill_in_survey = {
            'text_variable': "value",
            'multiplechoice_variable': "choice1",
            'multiselect_var': [],
            'password_var': "password_val",
            'float_var': 0,
            'integer_var': 12
        }
        expected_fill_in_survey = {
            'textarea_var': "textarea_value",
        }

        new_survey_config = {
            'text_variable': False,
            'multiplechoice_variable': False,
            'multiselect_var': False,
            'textarea_var': True,
            'password_var': False,
            'float_var': False,
            'integer_var': False
        }
        self.test_request.operation.switch_survey_fields_enable_from_dict(new_survey_config)
        self.test_request.refresh_from_db()
        self.assertDictEqual(self.test_request.fill_in_survey, expected_fill_in_survey)
        self.assertDictEqual(self.test_request.admin_fill_in_survey, expected_admin_fill_in_survey)
