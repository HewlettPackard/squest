from rest_framework import status
from rest_framework.reverse import reverse_lazy

from profiles.models import RequestNotification
from tests.test_profiles.base.base_test_request_notification_filter import BaseTestRequestNotification
from tests.utils import check_data_in_dict


class TestApiRequestNotificationFilterDetails(BaseTestRequestNotification):

    def setUp(self):
        super(TestApiRequestNotificationFilterDetails, self).setUp()
        self.kwargs = {
            'pk': self.request_notification_filter_test.id
        }
        self.get_notification_filter_details_url = reverse_lazy('api_request_notification_filter_details', kwargs=self.kwargs)
        self.expected_data = {
            'id': self.request_notification_filter_test.id,
            'name': self.request_notification_filter_test.name,
            'profile': self.request_notification_filter_test.profile.id,
            'services': list(self.request_notification_filter_test.services.all()),
            'operations': list(self.request_notification_filter_test.operations.all()),
            'request_states': self.request_notification_filter_test.request_states,
            'when': self.request_notification_filter_test.when,
        }
        self.expected_data_list = [self.expected_data]

    def test_admin_get_notification_filter_detail(self):
        response = self.client.get(self.get_notification_filter_details_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data_list = [response.data]
        check_data_in_dict(self, self.expected_data_list, data_list)

    def test_admin_cannot_get_notification_filter_detail_of_another_user(self):
        self.client.force_login(self.superuser_2)
        response = self.client.get(self.get_notification_filter_details_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_customer_can_get_notification_filter_detail(self):
        self.client.force_login(user=self.standard_user)
        request_notification_filter_test = RequestNotification.objects.create(name="request_test_filter_4",
                                                                              profile=self.standard_user.profile)
        self.kwargs["pk"] = request_notification_filter_test.id
        response = self.client.get(self.get_notification_filter_details_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_get_request_details_when_logout(self):
        self.client.logout()
        response = self.client.get(self.get_notification_filter_details_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
