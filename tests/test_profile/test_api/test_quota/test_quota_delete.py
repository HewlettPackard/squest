from rest_framework import status
from rest_framework.reverse import reverse

from profiles.models import Quota
from tests.test_profile.test_quota.base_test_quota import BaseTestQuota


class TestApiQuotaDelete(BaseTestQuota):

    def setUp(self):
        super(TestApiQuotaDelete, self).setUp()
        self.quota_to_delete_id = self.test_quota_attribute_cpu.id
        self.kwargs = {
            'pk': self.quota_to_delete_id
        }
        self.delete_quota_url = reverse('api_quota_details', kwargs=self.kwargs)

    def test_admin_delete_quota(self):
        quota_count = Quota.objects.count()
        response = self.client.delete(self.delete_quota_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(quota_count - 1, Quota.objects.count())
        self.assertFalse(Quota.objects.filter(id=self.quota_to_delete_id).exists())

    def test_customer_cannot_delete_quota(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.delete(self.delete_quota_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_delete_quota_when_logout(self):
        self.client.logout()
        response = self.client.delete(self.delete_quota_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
