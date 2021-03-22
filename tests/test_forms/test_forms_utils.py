from service_catalog.forms import utils
from tests.base import BaseTest


class TestServiceRequestForm(BaseTest):

    def setUp(self):
        super(TestServiceRequestForm, self).setUp()

    def test_get_choices_from_string(self):
        test_string = "choice1\nchoice2\nchoice3"
        expected_value = [("choice1", "choice1"), ("choice2", "choice2"), ("choice3", "choice3")]
        self.assertEquals(expected_value, utils.get_choices_from_string(test_string))
