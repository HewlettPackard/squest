from rest_framework import status
from rest_framework.reverse import reverse_lazy

from profiles.models import RequestNotification
from tests.test_profiles.base.base_test_request_notification_filter import BaseTestRequestNotificationAPI

from tests.utils import check_data_in_dict


class TestApiRequestNotificationFilterPatch(BaseTestRequestNotificationAPI):

    def setUp(self):
        super(TestApiRequestNotificationFilterPatch, self).setUp()
        self.patch_data = {
            'services': [self.service_test.id, self.service_test_2.id],
        }
        self.kwargs = {
            'pk': self.request_notification_filter_test.id
        }
        self.get_notification_filter_details_url = reverse_lazy('api_request_notification_filter_details',
                                                                kwargs=self.kwargs)
        self.expected_data = {
            'id': self.request_notification_filter_test.id,
            'name': self.request_notification_filter_test.name,
            'profile': self.request_notification_filter_test.profile.id,
            'services': self.patch_data['services'],
            'operations': list(self.request_notification_filter_test.operations.all()),
            'request_states': self.request_notification_filter_test.request_states,
            'when': self.request_notification_filter_test.when,
        }

    def test_admin_patch_notification_filter(self):
        response = self.client.patch(self.get_notification_filter_details_url, data=self.patch_data,
                                     format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        check_data_in_dict(self, [self.expected_data], [response.data])

    def test_customer_can_patch_notification_filter(self):
        self.client.force_login(user=self.standard_user)

        request_notification_filter_test = RequestNotification.objects.create(name="request_test_filter_4",
                                                                              profile=self.standard_user.profile)
        self.kwargs["pk"] = request_notification_filter_test.id

        response = self.client.patch(self.get_notification_filter_details_url, data=self.patch_data,
                                     format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_patch_notification_filter_when_logout(self):
        self.client.logout()
        response = self.client.patch(self.get_notification_filter_details_url, data=self.patch_data,
                                     format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
