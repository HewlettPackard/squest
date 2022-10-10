from rest_framework import status
from rest_framework.reverse import reverse

from profiles.models import RequestNotification
from tests.test_profile.base_test_profile import BaseTestProfile


class TestApiRequestNotificationFilterList(BaseTestProfile):

    def setUp(self):
        super(TestApiRequestNotificationFilterList, self).setUp()
        self.get_notification_filter_list_url = reverse('api_request_notification_filter_list_create')

    def test_admin_can_get_his_notification_filters(self):
        response = self.client.get(self.get_notification_filter_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], RequestNotification.objects.filter(profile=self.superuser.profile.id).count())

    def test_customer_cannot_get_notification_filter_list(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.get_notification_filter_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_get_notification_filter_list_when_logout(self):
        self.client.logout()
        response = self.client.get(self.get_notification_filter_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
