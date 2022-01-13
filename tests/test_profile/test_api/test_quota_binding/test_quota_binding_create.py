from rest_framework import status
from rest_framework.reverse import reverse

from profiles.models import Quota
from tests.test_profile.test_quota.base_test_quota import BaseTestQuota
from tests.utils import check_data_in_dict


class TestApiQuotaBindingCreate(BaseTestQuota):

    def setUp(self):
        super(TestApiQuotaBindingCreate, self).setUp()
        test_new_quota = Quota.objects.create(name="test")
        self.post_data = {
            'billing_group': self.test_billing_group.id,
            'quota': test_new_quota.id,
            'limit': 50
        }
        self.create_quota_binding_url = reverse('api_quota_binding_list_create')

    def _create_quota_binding(self):
        response = self.client.post(self.create_quota_binding_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        check_data_in_dict(self, [self.post_data], [response.data])

    def _create_quota_binding_failed(self, status_error=status.HTTP_400_BAD_REQUEST):
        response = self.client.post(self.create_quota_binding_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status_error)

    def test_admin_post_quota_binding(self):
        self._create_quota_binding()

    def test_cannot_post_the_same_quota_binding(self):
        self._create_quota_binding()
        self._create_quota_binding_failed()

    def test_customer_cannot_post_quota_binding(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.post(self.create_quota_binding_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_post_quota_binding_when_logout(self):
        self.client.logout()
        response = self.client.post(self.create_quota_binding_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
