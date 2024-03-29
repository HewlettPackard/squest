from rest_framework import status
from rest_framework.reverse import reverse_lazy

from profiles.models import InstanceNotification
from tests.test_profiles.base.base_test_instance_notification_filter import BaseTestInstanceNotificationAPI



class TestApiInstanceNotificationFilterList(BaseTestInstanceNotificationAPI):
    def setUp(self):
        super(TestApiInstanceNotificationFilterList, self).setUp()
        self.get_notification_filter_list_url = reverse_lazy('api_instancenotification_list_create')

    def test_admin_can_get_his_notification_filters(self):
        response = self.client.get(self.get_notification_filter_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], InstanceNotification.objects.filter(profile=self.superuser.profile.id).count())

    def test_customer_can_get_notification_filter_list(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.get_notification_filter_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_get_notification_filter_list_when_logout(self):
        self.client.logout()
        response = self.client.get(self.get_notification_filter_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
