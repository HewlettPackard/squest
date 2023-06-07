from service_catalog.forms import AcceptRequestForm
from service_catalog.models import Request, Instance
from tests.test_service_catalog.base import BaseTest

class TestAcceptRequestForm(BaseTest):

    def setUp(self):
        super(TestAcceptRequestForm, self).setUp()

        self.job_template_test.survey = {
            "name": "test-survey",
            "description": "test-survey-description",
            "spec": [
                {
                    "choices": "",
                    "default": "this_is_default_from_tower",
                    "max": 1024,
                    "min": 0,
                    "new_question": True,
                    "question_description": "",
                    "question_name": "String variable",
                    "required": False,
                    "type": "text",
                    "variable": "text_variable"
                }
            ]
        }
        self.job_template_test.save()
        data = {
            'text_variable': 'variable_set_by_user'
        }
        self.test_instance = Instance.objects.create(name="test_instance_1",
                                                     service=self.service_test,
                                                     spoc=self.standard_user)
        self.test_request = Request.objects.create(fill_in_survey=data,
                                                   instance=self.test_instance,
                                                   operation=self.create_operation_test,
                                                   user=self.standard_user)

    def test_admin_can_blank_non_required_field(self):
        parameters = {
            'request': self.test_request
        }
        data = {
            'squest_instance_name': self.test_request.instance.name,
            'billing_group_id': None,
            'text_variable': '',
        }
        form = AcceptRequestForm(self.superuser, data, **parameters)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(self.test_request.fill_in_survey["text_variable"], "")
