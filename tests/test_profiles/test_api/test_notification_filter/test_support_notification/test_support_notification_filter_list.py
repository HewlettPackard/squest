from rest_framework import status
from rest_framework.reverse import reverse_lazy

from profiles.models import InstanceNotification
from tests.test_profiles.base.base_test_support_notification_filter import BaseTestInstanceNotification



class TestApiSupportNotificationFilterList(BaseTestInstanceNotification):

    def setUp(self):
        super(TestApiSupportNotificationFilterList, self).setUp()
        self.get_notification_filter_list_url = reverse_lazy('api_support_notification_filter_list_create')

    def test_admin_can_get_his_notification_filters(self):
        response = self.client.get(self.get_notification_filter_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], InstanceNotification.objects.filter(profile=self.superuser.profile.id).count())

    def test_customer_cannot_get_notification_filter_list(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.get_notification_filter_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_get_notification_filter_list_when_logout(self):
        self.client.logout()
        response = self.client.get(self.get_notification_filter_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
