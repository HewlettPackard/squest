from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_profile.base_test_profile import BaseTestProfile
from tests.utils import check_data_in_dict


class TestApiSupportNotificationFilterPatch(BaseTestProfile):

    def setUp(self):
        super(TestApiSupportNotificationFilterPatch, self).setUp()
        self.patch_data = {
            'services': [self.service_test.id, self.service_test_2.id],
        }
        self.kwargs = {
            'pk': self.support_notification_filter_test.id
        }
        self.get_notification_filter_details_url = reverse('api_support_notification_filter_details', kwargs=self.kwargs)
        self.expected_data = {
            'id': self.support_notification_filter_test.id,
            'name': self.support_notification_filter_test.name,
            'profile': self.support_notification_filter_test.profile.id,
            'services': self.patch_data['services'],
            'instance_states': self.support_notification_filter_test.instance_states,
            'when': self.support_notification_filter_test.when,
        }

    def test_admin_patch_notification_filter(self):
        response = self.client.patch(self.get_notification_filter_details_url, data=self.patch_data,
                                     content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        check_data_in_dict(self, [self.expected_data], [response.data])

    def test_customer_cannot_patch_notification_filter(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.patch(self.get_notification_filter_details_url, data=self.patch_data,
                                     content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_patch_notification_filter_when_logout(self):
        self.client.logout()
        response = self.client.patch(self.get_notification_filter_details_url, data=self.patch_data,
                                     content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
