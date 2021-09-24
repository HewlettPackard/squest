from service_catalog.forms import utils
from tests.test_service_catalog.base import BaseTest


class TestServiceRequestForm(BaseTest):

    def setUp(self):
        super(TestServiceRequestForm, self).setUp()

    def test_get_choices_from_string(self):
        test_string = "choice1\nchoice2\nchoice3"
        expected_value = [("", "Select an option"), ("choice1", "choice1"), ("choice2", "choice2"), ("choice3", "choice3")]
        self.assertEquals(expected_value, utils.get_choices_from_string(test_string))

    def test_create_form_fields(self):
        expected_result = len(self.testing_survey["spec"])
        self.assertEquals(len(utils.get_fields_from_survey(self.testing_survey)), expected_result)

    def test_set_default_fields_values(self):
        form = utils.get_fields_from_survey(self.testing_survey)
        expected_results = ["", "choice1", ["multiselect_2", "multiselect_3"], "textarea_val", None, 1, 1.5]
        for field, expected_result in zip(form.values(), expected_results):
            self.assertEquals(field.initial, expected_result)
