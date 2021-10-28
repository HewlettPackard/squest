from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.utils import check_data_in_dict


class TestApiBillingGroupCreate(BaseTestRequest):

    def setUp(self):
        super(TestApiBillingGroupCreate, self).setUp()
        self.post_data = {
            'name': "My new billing group",
            'user_set': [self.standard_user.id, self.standard_user_2.id]
        }
        self.create_billing_group_url = reverse('api_billing_group_list_create')

    def _create_billing_group(self):
        response = self.client.post(self.create_billing_group_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        check_data_in_dict(self, [self.post_data], [response.data])

    def _create_billing_group_failed(self, status_error=status.HTTP_400_BAD_REQUEST):
        response = self.client.post(self.create_billing_group_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status_error)

    def test_admin_post_billing_group(self):
        self._create_billing_group()

    def test_cannot_post_billing_group_with_existing_name(self):
        self._create_billing_group()
        self._create_billing_group_failed()

    def test_customer_cannot_post_billing_group(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.post(self.create_billing_group_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_post_billing_group_when_logout(self):
        self.client.logout()
        response = self.client.post(self.create_billing_group_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
