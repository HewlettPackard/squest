from rest_framework import status
from rest_framework.reverse import reverse

from profiles.api.serializers.user_serializers import UserSerializerNested
from service_catalog.models import Request, RequestState
from tests.test_service_catalog.base_test_request import BaseTestRequestAPI
from tests.utils import check_data_in_dict


class TestApiRequestPut(BaseTestRequestAPI):

    def setUp(self):
        super(TestApiRequestPut, self).setUp()
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
        self.put_data = {
            'fill_in_survey': dict(),
            'tower_job_id': 6,
            'state': RequestState.ON_HOLD,
            'operation': self.update_operation_test.id,
            'user': {'id': self.standard_user.id}
        }
        self.kwargs = {
            'pk': self.test_request_standard_user_1.id
        }
        self.get_request_details_url = reverse('api_request_details', kwargs=self.kwargs)

    def test_admin_put_on_request(self):
        response = self.client.put(self.get_request_details_url, data=self.put_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = self.put_data
        expected['user'] = UserSerializerNested(instance=self.standard_user).data
        check_data_in_dict(self, [expected], [response.data])

    def test_admin_cannot_put_on_request_not_full(self):
        self.put_data.pop('operation')
        response = self.client.put(self.get_request_details_url, data=self.put_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_customer_cannot_put_on_his_request(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.put(self.get_request_details_url, data=self.put_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_put_on_non_own_request(self):
        self.client.force_login(user=self.standard_user)
        self.kwargs['pk'] = self.test_request_standard_user_2.id
        url = reverse('api_request_details', kwargs=self.kwargs)
        response = self.client.put(url, data=self.put_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_put_request_when_logout(self):
        self.client.logout()
        response = self.client.put(self.get_request_details_url, data=self.put_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _check_data(self, expected_data_list, data_list):
        for expected_data, data in zip(expected_data_list, data_list):
            for key_var, val_var in expected_data.items():
                self.assertIn(key_var, data.keys())
                self.assertEqual(val_var, data[key_var])
