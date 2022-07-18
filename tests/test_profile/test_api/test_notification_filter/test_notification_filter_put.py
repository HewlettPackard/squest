from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_profile.base_test_profile import BaseTestProfile
from tests.utils import check_data_in_dict


class TestApiNotificationFilterPatch(BaseTestProfile):

    def setUp(self):
        super(TestApiNotificationFilterPatch, self).setUp()
        self.put_data = {
            'name': 'new_name',
            'services': [self.service_test.id, self.service_test_2.id],
        }
        self.kwargs = {
            'pk': self.notification_filter_test.id
        }
        self.get_notification_filter_details_url = reverse('api_notification_filter_details', kwargs=self.kwargs)
        self.expected_data = {
            'id': self.notification_filter_test.id,
            'name': self.put_data['name'],
            'profile': self.notification_filter_test.profile.id,
            'services': self.put_data['services'],
            'operations': list(self.notification_filter_test.operations.all()),
            'request_states': self.notification_filter_test.request_states,
            'instance_states': self.notification_filter_test.instance_states,
            'when': self.notification_filter_test.when,
        }

    def test_admin_put_notification_filter(self):
        response = self.client.put(self.get_notification_filter_details_url, data=self.put_data,
                                   content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        check_data_in_dict(self, [self.expected_data], [response.data])

    def test_customer_cannot_put_notification_filter(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.put(self.get_notification_filter_details_url, data=self.put_data,
                                   content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_put_notification_filter_when_logout(self):
        self.client.logout()
        response = self.client.put(self.get_notification_filter_details_url, data=self.put_data,
                                   content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
