from rest_framework import status
from rest_framework.reverse import reverse

from profiles.api.serializers.billing_group_serializers import BillingGroupWriteSerializer
from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.utils import check_data_in_dict


class TestApiBillingGroupPatch(BaseTestRequest):

    def setUp(self):
        super(TestApiBillingGroupPatch, self).setUp()
        self.put_data = {
            'name': "My new billing group",
            'user_set': [self.standard_user.id, self.standard_user_2.id]
        }
        self.kwargs = {
            'pk': self.test_billing_group.id
        }
        self.get_billing_group_details_url = reverse('api_billing_group_details', kwargs=self.kwargs)
        self.expected_data = BillingGroupWriteSerializer(self.test_billing_group).data
        self.expected_data['name'] = "My new billing group"
        self.expected_data['user_set'] = [self.standard_user.id, self.standard_user_2.id]

    def test_admin_put_billing_group(self):
        response = self.client.put(self.get_billing_group_details_url, data=self.put_data,
                                   content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        check_data_in_dict(self, [self.expected_data], [response.data])

    def test_customer_cannot_put_billing_group(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.put(self.get_billing_group_details_url, data=self.put_data,
                                   content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_put_billing_group_when_logout(self):
        self.client.logout()
        response = self.client.put(self.get_billing_group_details_url, data=self.put_data,
                                   content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
