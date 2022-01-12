from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_profile.test_quota.base_test_quota import BaseTestQuota
from tests.utils import check_data_in_dict


class TestApiQuotaDetails(BaseTestQuota):

    def setUp(self):
        super(TestApiQuotaDetails, self).setUp()
        self.kwargs = {
            'pk': self.test_quota_attribute_cpu.id
        }
        self.get_quota_details_url = reverse('api_quota_details', kwargs=self.kwargs)
        self.expected_data = {
            'id': self.test_quota_attribute_cpu.id,
            'name': self.test_quota_attribute_cpu.name,
            'attribute_definitions': [attribute.id for attribute in self.test_quota_attribute_cpu.attribute_definitions.all()],
        }
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
