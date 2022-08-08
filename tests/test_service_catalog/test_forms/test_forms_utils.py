from service_catalog.forms import utils, FormUtils
from tests.test_service_catalog.base import BaseTest


class TestServiceRequestForm(BaseTest):

    def setUp(self):
        super(TestServiceRequestForm, self).setUp()
        self.testing_survey_with_validator = FormUtils.apply_user_validator_to_survey(
            job_template_survey=self.testing_survey,
            operation_survey=self.create_operation_test.tower_survey_fields)

    def test_get_choices_as_tuples_list(self):
        test_string = "choice1\nchoice2\nchoice3"
        expected_value = [("", "Select an option"), ("choice1", "choice1"), ("choice2", "choice2"),
                          ("choice3", "choice3")]
        self.assertEqual(expected_value, utils.get_choices_as_tuples_list(test_string))
        test_list = ["choice1", "choice2", "choice3"]
        self.assertEqual(expected_value, utils.get_choices_as_tuples_list(test_list))

    def test_create_form_fields(self):
        expected_result = len(self.testing_survey_with_validator["spec"])
        self.assertEqual(len(utils.get_fields_from_survey(self.testing_survey_with_validator)), expected_result)

    def test_set_default_fields_values(self):
        form = utils.get_fields_from_survey(self.testing_survey_with_validator)
        expected_results = ["", "choice1", ["multiselect_2", "multiselect_3"], "textarea_val", None, 1, 1.5]
        for field, expected_result in zip(form.values(), expected_results):
            self.assertEqual(field.initial, expected_result)
