from rest_framework import status
from rest_framework.reverse import reverse

from profiles.models import Quota
from tests.test_profile.test_quota.base_test_quota import BaseTestQuota


class TestApiQuotaList(BaseTestQuota):

    def setUp(self):
        super(TestApiQuotaList, self).setUp()
        self.get_quota_list_url = reverse('api_quota_list_create')

    def test_get_all_quota(self):
        response = self.client.get(self.get_quota_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Quota.objects.count())

    def test_customer_cannot_get_quota_list(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.get_quota_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_get_quota_list_when_logout(self):
        self.client.logout()
        response = self.client.get(self.get_quota_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
