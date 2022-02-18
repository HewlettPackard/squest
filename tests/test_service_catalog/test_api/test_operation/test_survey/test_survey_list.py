from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestOperationSurveyList(BaseTestRequest):

    def setUp(self):
        super(TestOperationSurveyList, self).setUp()
        self.kwargs = {'service_id': self.service_test.id, 'pk': self.test_request.operation.id}
        self.get_operation_survey_list_url = reverse('api_operation_survey_list_update', kwargs=self.kwargs)

    def test_list_survey(self):
        response = self.client.get(self.get_operation_survey_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), self.test_request.operation.tower_survey_fields.count())

    def test_customer_cannot_list_survey(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.get_operation_survey_list_url, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_cannot_list_survey_when_logout(self):
        self.client.logout()
        response = self.client.post(self.get_operation_survey_list_url, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
