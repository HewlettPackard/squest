from rest_framework import status
from rest_framework.reverse import reverse

from profiles.models import QuotaBinding
from tests.test_profile.test_quota.base_test_quota import BaseTestQuota


class TestApiQuotaBindingDelete(BaseTestQuota):

    def setUp(self):
        super(TestApiQuotaBindingDelete, self).setUp()
        self.quota_to_delete_id = self.test_quota_binding.id
        self.kwargs = {
            'pk': self.quota_to_delete_id
        }
        self.delete_quota_url = reverse('api_quota_binding_details', kwargs=self.kwargs)

    def test_admin_delete_quota(self):
        quota_count = QuotaBinding.objects.count()
        response = self.client.delete(self.delete_quota_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(quota_count - 1, QuotaBinding.objects.count())
        self.assertFalse(QuotaBinding.objects.filter(id=self.quota_to_delete_id).exists())

    def test_customer_cannot_delete_quota(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.delete(self.delete_quota_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_delete_quota_when_logout(self):
        self.client.logout()
        response = self.client.delete(self.delete_quota_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
