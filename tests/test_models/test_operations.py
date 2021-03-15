from tests.base import BaseTest


class CatalogViewTestCase(BaseTest):

    def setUp(self):
        super(CatalogViewTestCase, self).setUp()

    def test_survey_from_job_template_is_copied_on_create(self):
        expected_result = {
            "text_variable": True,
            "multiplechoice_variable": True
        }

        self.assertEquals(self.create_operation_test.enabled_survey_fields, expected_result)
