from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_profile.test_quota.base_test_quota import BaseTestQuota
from tests.utils import check_data_in_dict


class TestApiQuotaCreate(BaseTestQuota):

    def setUp(self):
        super(TestApiQuotaCreate, self).setUp()
        self.post_data = {
            'name': "My new quota",
            'attribute_definitions': [self.memory_attributes.first().id, self.cpu_attributes.first().id]
        }
        self.create_quota_url = reverse('api_quota_list_create')

    def _create_quota(self):
        response = self.client.post(self.create_quota_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        check_data_in_dict(self, [self.post_data], [response.data])

    def _create_quota_failed(self, status_error=status.HTTP_400_BAD_REQUEST):
        response = self.client.post(self.create_quota_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status_error)

    def test_admin_post_quota(self):
        self._create_quota()

    def test_cannot_post_quota_with_existing_name(self):
        self._create_quota()
        self._create_quota_failed()

    def test_customer_cannot_post_quota(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.post(self.create_quota_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_post_quota_when_logout(self):
        self.client.logout()
        response = self.client.post(self.create_quota_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
