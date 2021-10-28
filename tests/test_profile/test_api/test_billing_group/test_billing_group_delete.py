from rest_framework import status
from rest_framework.reverse import reverse

from profiles.models import BillingGroup
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestApiBillingGroupDelete(BaseTestRequest):

    def setUp(self):
        super(TestApiBillingGroupDelete, self).setUp()
        self.billing_group_to_delete_id = self.test_billing_group.id
        self.kwargs = {
            'pk': self.billing_group_to_delete_id
        }
        self.delete_billing_group_url = reverse('api_billing_group_details', kwargs=self.kwargs)

    def test_admin_delete_billing_group(self):
        billing_group_count = BillingGroup.objects.count()
        response = self.client.delete(self.delete_billing_group_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(billing_group_count - 1, BillingGroup.objects.count())
        self.assertFalse(BillingGroup.objects.filter(id=self.billing_group_to_delete_id).exists())

    def test_customer_cannot_delete_billing_group(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.delete(self.delete_billing_group_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_delete_billing_group_when_logout(self):
        self.client.logout()
        response = self.client.delete(self.delete_billing_group_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
