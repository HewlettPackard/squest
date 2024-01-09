import json
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status

from service_catalog.models import InstanceState
from tests.setup import SetupInstanceAPI

from django.test import override_settings


class TestSurveyValidatorDay1API(SetupInstanceAPI):

    def setUp(self):
        SetupInstanceAPI.setUp(self)
        self.operation_create_1.validators = 'survey_test.Validator1,survey_test.Validator2'
        self.operation_create_1.save()
        self.superuser = User.objects.create_superuser(username='superuser')
        self.client.force_login(user=self.superuser)
        url_kwargs = {
            'service_id': self.operation_create_1.service.id,
            'pk': self.operation_create_1.id,
        }
        self.url = reverse('api_service_request_create', kwargs=url_kwargs)

    @override_settings(SURVEY_VALIDATOR_PATH='tests/test_plugins/survey_validators_test')
    def test_injected_data_are_good(self):
        self.operation_create_1.validators = 'survey_test.ValidatorDay1'
        self.operation_create_1.save()
        data = {
            'squest_instance_name': 'instance test',
            'request_comment': 'comment day1',
            'quota_scope': self.org1.id,
            'fill_in_survey': {
                'vcpu': 1,
                'ram': 1
            },
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        loaded_content = json.loads(response.content)
        self.assertEqual(
            loaded_content,
            {'__all__': ["Everything is good, it's just a message to be sure that code was executed"]}
        )


class TestSurveyValidatorDay2API(SetupInstanceAPI):

    def setUp(self):
        SetupInstanceAPI.setUp(self)
        self.operation_update_1.validators = 'survey_test.Validator1,survey_test.Validator2'
        self.operation_update_1.save()
        self.superuser = User.objects.create_superuser(username='superuser')
        self.client.force_login(user=self.superuser)
        self.instance_1_org1.state = InstanceState.AVAILABLE
        self.instance_1_org1.service = self.operation_update_1.service
        self.instance_1_org1.save()
        url_kwargs = {
            'instance_id': self.instance_1_org1.id,
            'operation_id': self.operation_update_1.id,
        }

        self.url = reverse('api_operation_request_create', kwargs=url_kwargs)

    @override_settings(SURVEY_VALIDATOR_PATH='tests/test_plugins/survey_validators_test')
    def test_injected_data_are_good(self):
        self.operation_update_1.validators = 'survey_test.ValidatorDay2'
        self.operation_update_1.save()
        data = {
            'request_comment': 'comment day2',
            'fill_in_survey': {
                'vcpu': 1,
                'ram': 1
            },
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        loaded_content = json.loads(response.content)
        self.assertEqual(
            loaded_content,
            {'__all__': ["Everything is good, it's just a message to be sure that code was executed"]}
        )
