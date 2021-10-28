from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.utils import check_data_in_dict


class TestApiBillingGroupDetails(BaseTestRequest):

    def setUp(self):
        super(TestApiBillingGroupDetails, self).setUp()
        self.kwargs = {
            'pk': self.test_billing_group.id
        }
        self.get_billing_group_details_url = reverse('api_billing_group_details', kwargs=self.kwargs)
        self.expected_data = {
            'id': self.test_billing_group.id,
            'name': self.test_billing_group.name,
            'user_set': list(self.test_billing_group.user_set.all()),
        }
        self.expected_data_list = [self.expected_data]

    def test_admin_get_billing_group_detail(self):
        response = self.client.get(self.get_billing_group_details_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data_list = [response.data]
        check_data_in_dict(self, self.expected_data_list, data_list)

    def test_customer_cannot_get_billing_group_detail(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.get_billing_group_details_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_get_request_details_when_logout(self):
        self.client.logout()
        response = self.client.get(self.get_billing_group_details_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
