from tests.base import BaseTest


class TestOperation(BaseTest):

    def setUp(self):
        super(TestOperation, self).setUp()

    def test_survey_from_job_template_is_copied_on_create(self):
        expected_result = {
            "text_variable": True,
            "multiplechoice_variable": False
        }

        self.assertEquals(self.create_operation_test.enabled_survey_fields, expected_result)
