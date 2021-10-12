from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import Request, RequestState
from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.utils import check_data_in_dict


class TestApiRequestPatch(BaseTestRequest):

    def setUp(self):
        super(TestApiRequestPatch, self).setUp()
        self.test_request_standard_user_1 = Request.objects.create(
            fill_in_survey={},
            instance=self.test_instance,
            operation=self.create_operation_test,
            user=self.standard_user
        )
        self.test_request_standard_user_2 = Request.objects.create(
            fill_in_survey={},
            instance=self.test_instance,
            operation=self.create_operation_test,
            user=self.standard_user_2
        )
        self.patch_data = {
            'operation': self.update_operation_test.id,
            'state': RequestState.NEED_INFO,
        }
        self.kwargs = {
            'pk': self.test_request_standard_user_1.id
        }
        self.get_request_details_url = reverse('api_request_details', kwargs=self.kwargs)
        self.expected_data = {
            'id': self.test_request_standard_user_1.id,
            'fill_in_survey': self.test_request_standard_user_1.fill_in_survey,
            'tower_job_id': self.test_request_standard_user_1.tower_job_id,
            'state': RequestState.NEED_INFO,
            'operation': self.update_operation_test.id,
            'user': self.test_request_standard_user_1.user.id
        }

    def test_admin_patch_request(self):
        response = self.client.patch(self.get_request_details_url, data=self.patch_data,
                                     content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        check_data_in_dict(self, [self.expected_data], [response.data])

    def test_customer_cannot_patch_his_request(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.patch(self.get_request_details_url, data=self.patch_data,
                                     content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_patch_non_own_request(self):
        self.client.force_login(user=self.standard_user)
        self.kwargs['pk'] = self.test_request_standard_user_2.id
        url = reverse('api_request_details', kwargs=self.kwargs)
        response = self.client.patch(url, data=self.patch_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_patch_request_when_loggout(self):
        self.client.logout()
        response = self.client.patch(self.get_request_details_url, data=self.patch_data,
                                     content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def check_data_in_dict(self, expected_data_list, data_list):
        for expected_data, data in zip(expected_data_list, data_list):
            for key_var, val_var in expected_data.items():
                self.assertIn(key_var, data.keys())
                self.assertEquals(val_var, data[key_var])
