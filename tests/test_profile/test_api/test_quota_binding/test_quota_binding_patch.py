from rest_framework import status
from rest_framework.reverse import reverse

from profiles.api.serializers.quota_binding_serializers import QuotaBindingWriteSerializer
from tests.test_profile.test_quota.base_test_quota import BaseTestQuota
from tests.utils import check_data_in_dict


class TestApiQuotaBindingPatch(BaseTestQuota):

    def setUp(self):
        super(TestApiQuotaBindingPatch, self).setUp()
        self.patch_data = {
            'limit': 50
        }
        self.kwargs = {
            'pk': self.test_quota_binding.id
        }
        self.get_quota_details_url = reverse('api_quota_binding_details', kwargs=self.kwargs)
        self.expected_data = QuotaBindingWriteSerializer(self.test_quota_binding).data
        self.expected_data['limit'] = 50

    def test_admin_patch_quota(self):
        response = self.client.patch(self.get_quota_details_url, data=self.patch_data,
                                     content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        check_data_in_dict(self, [self.expected_data], [response.data])

    def test_customer_cannot_patch_quota(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.patch(self.get_quota_details_url, data=self.patch_data,
                                     content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_patch_quota_when_logout(self):
        self.client.logout()
        response = self.client.patch(self.get_quota_details_url, data=self.patch_data,
                                     content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
