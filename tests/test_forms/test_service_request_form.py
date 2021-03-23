from http import HTTPStatus

from django.urls import reverse

from service_catalog.forms import ServiceRequestForm, FormUtils
from tests.base import BaseTest


class TestServiceRequestForm(BaseTest):

    def setUp(self):
        super(TestServiceRequestForm, self).setUp()

    def test_get_available_fields(self):
        expected_result = {
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

        self.assertEquals(expected_result,
                          FormUtils.get_available_fields(job_template_survey=self.job_template_test.survey,
                                                         operation_survey=self.create_operation_test.enabled_survey_fields))

    def test_create_request(self):
        url_args = {
            'service_id': self.service_test.id,
        }
        url = reverse('customer_service_request', kwargs=url_args)
        response = self.client.post(
            url, data={"text_variable": "value"}
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

