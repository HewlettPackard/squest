from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import OperationType
from service_catalog.models.tower_survey_field import TowerSurveyField
from tests.test_service_catalog.base_test_request import BaseTestRequestAPI
from tests.utils import check_data_in_dict


class TestApiOperationCreate(BaseTestRequestAPI):

    def setUp(self):
        super(TestApiOperationCreate, self).setUp()
        self.kwargs = {'service_id': self.service_test.id}
        self.post_data = {
            'name': "My new name",
            'description': "My new description",
            'type': OperationType.UPDATE,
            'auto_accept': False,
            'auto_process': False,
            'process_timeout_second': 60,
            'job_template': self.job_template_test.id,
            'extra_vars': {"test": "test"}
        }
        self.get_operation_details_url = reverse('api_operation_list_create', kwargs=self.kwargs)

    def test_admin_post_operation(self):
        number_tower_survey_field_before = TowerSurveyField.objects.all().count()
        response = self.client.post(self.get_operation_details_url, data=self.post_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        check_data_in_dict(self, [self.post_data], [response.data])
        number_field_in_survey = len(self.job_template_test.survey["spec"])
        self.assertEqual(number_tower_survey_field_before + number_field_in_survey,
                         TowerSurveyField.objects.all().count())

    def test_admin_cannot_post_on_operation_not_full(self):
        self.post_data.pop('name')
        response = self.client.post(self.get_operation_details_url, data=self.post_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_customer_cannot_post_operation(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.post(self.get_operation_details_url, data=self.post_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_post_operation_when_logout(self):
        self.client.logout()
        response = self.client.post(self.get_operation_details_url, data=self.post_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_post_operation_with_non_json_as_extra_vars(self):
        self.post_data['extra_vars'] = 'test'
        response = self.client.post(self.get_operation_details_url, data=self.post_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
