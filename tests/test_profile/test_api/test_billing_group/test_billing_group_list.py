from rest_framework import status
from rest_framework.reverse import reverse

from profiles.models import BillingGroup
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestApiBillingGroupList(BaseTestRequest):

    def setUp(self):
        super(TestApiBillingGroupList, self).setUp()
        self.get_billing_group_list_url = reverse('api_billing_group_list_create')

    def test_get_all_billing_groups(self):
        response = self.client.get(self.get_billing_group_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), BillingGroup.objects.count())

    def test_customer_cannot_get_billing_group_list(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.get_billing_group_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_get_billing_group_list_when_logout(self):
        self.client.logout()
        response = self.client.get(self.get_billing_group_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
