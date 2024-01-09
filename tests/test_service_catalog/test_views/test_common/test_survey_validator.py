from django.contrib.auth.models import User
from django.urls import reverse

from service_catalog.models import InstanceState
from tests.setup import SetupInstance

from django.test import override_settings


class TestSurveyValidatorDay1UI(SetupInstance):

    def setUp(self):
        SetupInstance.setUp(self)

        self.operation_create_1.validators = 'survey_test.Validator1,survey_test.Validator2'
        self.operation_create_1.save()
        self.superuser = User.objects.create_superuser(username='superuser')
        self.client.force_login(user=self.superuser)
        args = {
            "service_id": self.operation_create_1.service.id,
            "operation_id": self.operation_create_1.id
        }
        self.url = reverse('service_catalog:request_service', kwargs=args)

        data_form1 = {
            "0-name": "instance test",
            "0-quota_scope": self.org1.id,
            "service_request_wizard_view-current_step": "0",
        }

        response = self.client.post(self.url, data=data_form1)
        self.assertEqual(response.status_code, 200)

    @override_settings(SURVEY_VALIDATOR_PATH='tests/test_plugins/survey_validators_test')
    def test_injected_data_are_good(self):
        self.operation_create_1.validators = 'survey_test.ValidatorDay1'
        self.operation_create_1.save()
        data_form2 = {
            '1-request_comment': 'comment day1',
            "1-ram": 1,
            "1-vcpu": 1,
            "service_request_wizard_view-current_step": "1",
        }
        response = self.client.post(self.url, data=data_form2)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.context["form"].errors["__all__"][0],
                         "Everything is good, it's just a message to be sure that code was executed")

class TestSurveyValidatorDay2UI(SetupInstance):

    def setUp(self):
        SetupInstance.setUp(self)

        self.operation_update_1.validators = 'survey_test.Validator1,survey_test.Validator2'
        self.operation_update_1.save()
        self.superuser = User.objects.create_superuser(username='superuser')
        self.client.force_login(user=self.superuser)
        self.instance_1_org1.state = InstanceState.AVAILABLE
        self.instance_1_org1.service = self.operation_update_1.service
        self.instance_1_org1.save()
        args = {
            'instance_id': self.instance_1_org1.id,
            'operation_id': self.operation_update_1.id
        }
        self.url = reverse('service_catalog:instance_request_new_operation', kwargs=args)

    @override_settings(SURVEY_VALIDATOR_PATH='tests/test_plugins/survey_validators_test')
    def test_injected_data_are_good(self):
        self.operation_update_1.validators = 'survey_test.ValidatorDay2'
        self.operation_update_1.save()
        data = {
            'request_comment': 'comment day2',
            "vcpu": 1,
            "ram": 1
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.context["form"].errors["__all__"][0],
                         "Everything is good, it's just a message to be sure that code was executed")
