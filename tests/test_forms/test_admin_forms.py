from service_catalog.forms import AcceptRequestForm
from tests.base import BaseTest


class TestServiceRequestForm(BaseTest):

    def setUp(self):
        super(TestServiceRequestForm, self).setUp()

    def test_get_field_group(self):
        field_name = 'text_variable'
        enabled_field = {
            'text_variable': True,
            'multiplechoice_variable': False
        }
        expected_result = "User"
        self.assertEquals(expected_result, AcceptRequestForm._get_field_group(field_name, enabled_field))

        field_name = 'multiplechoice_variable'
        expected_result = "Admin"
        self.assertEquals(expected_result, AcceptRequestForm._get_field_group(field_name, enabled_field))
