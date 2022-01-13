from rest_framework import status
from rest_framework.reverse import reverse

from profiles.api.serializers.quota_binding_serializers import QuotaBindingSerializer
from tests.test_profile.test_quota.base_test_quota import BaseTestQuota
from tests.utils import check_data_in_dict


class TestApiQuotaBindingPatch(BaseTestQuota):

    def setUp(self):
        super(TestApiQuotaBindingPatch, self).setUp()
        self.put_data = {
            'billing_group': self.test_billing_group.id,
            'quota': self.test_quota_attribute_cpu.id,
            'limit': 50
        }
        self.kwargs = {
            'pk': self.test_quota_binding.id
        }
        self.get_quota_details_url = reverse('api_quota_binding_details', kwargs=self.kwargs)
        self.expected_data = QuotaBindingSerializer(self.test_quota_binding).data
        self.expected_data['billing_group'] = self.test_billing_group.id
        self.expected_data['quota'] = self.test_quota_attribute_cpu.id
        self.expected_data['limit'] = 50

    def test_admin_put_quota(self):
        response = self.client.put(self.get_quota_details_url, data=self.put_data,
                                   content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        check_data_in_dict(self, [self.expected_data], [response.data])

    def test_customer_cannot_put_quota(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.put(self.get_quota_details_url, data=self.put_data,
                                   content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_put_quota_when_logout(self):
        self.client.logout()
        response = self.client.put(self.get_quota_details_url, data=self.put_data,
                                   content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
