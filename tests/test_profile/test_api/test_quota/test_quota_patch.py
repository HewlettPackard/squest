from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_profile.test_quota.base_test_quota import BaseTestQuota
from tests.utils import check_data_in_dict


class TestApiQuotaPatch(BaseTestQuota):

    def setUp(self):
        super(TestApiQuotaPatch, self).setUp()
        self.patch_data = {
            'name': "My new quota",
        }
        self.kwargs = {
            'pk': self.test_quota_attribute_cpu.id
        }
        self.get_quota_details_url = reverse('api_quota_details', kwargs=self.kwargs)
        self.expected_data = {
            'name': "My new quota",
            'attribute_definitions': [attribute.id for attribute in self.test_quota_attribute_cpu.attribute_definitions.all()]
        }

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
