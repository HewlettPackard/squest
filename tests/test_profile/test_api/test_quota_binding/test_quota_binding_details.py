from rest_framework import status
from rest_framework.reverse import reverse

from profiles.api.serializers.quota_binding_serializers import QuotaBindingSerializer
from tests.test_profile.test_quota.base_test_quota import BaseTestQuota
from tests.utils import check_data_in_dict


class TestApiQuotaBindingDetails(BaseTestQuota):

    def setUp(self):
        super(TestApiQuotaBindingDetails, self).setUp()
        self.kwargs = {
            'pk': self.test_quota_binding.id
        }
        self.get_quota_details_url = reverse('api_quota_binding_details', kwargs=self.kwargs)
        self.test_quota_binding.refresh_from_db()
        self.expected_data = QuotaBindingSerializer(self.test_quota_binding).data
        self.expected_data_list = [self.expected_data]

    def test_admin_get_quota_detail(self):
        response = self.client.get(self.get_quota_details_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data_list = [response.data]
        check_data_in_dict(self, self.expected_data_list, data_list)

    def test_customer_cannot_get_quota_detail(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.get_quota_details_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_get_request_details_when_logout(self):
        self.client.logout()
        response = self.client.get(self.get_quota_details_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
