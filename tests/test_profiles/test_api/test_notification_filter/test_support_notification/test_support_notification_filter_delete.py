from rest_framework import status
from rest_framework.reverse import reverse_lazy

from profiles.models import InstanceNotification
from tests.test_profiles.base.base_test_support_notification_filter import BaseTestInstanceNotificationAPI


class TestApiSupportNotificationDelete(BaseTestInstanceNotificationAPI):

    def setUp(self):
        super(TestApiSupportNotificationDelete, self).setUp()
        self.notification_filter_to_delete_id = self.support_notification_filter_test.id
        self.kwargs = {
            'pk': self.notification_filter_to_delete_id
        }
        self.delete_notification_filter_url = reverse_lazy('api_support_notification_filter_details',
                                                           kwargs=self.kwargs)

    def test_admin_delete_notification_filter(self):
        notification_filter_count = InstanceNotification.objects.count()
        response = self.client.delete(self.delete_notification_filter_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(notification_filter_count - 1, InstanceNotification.objects.count())
        self.assertFalse(InstanceNotification.objects.filter(id=self.notification_filter_to_delete_id).exists())

    def test_admin_cannot_delete_notification_filter_of_another_user(self):
        self.client.force_login(user=self.superuser_2)
        response = self.client.delete(self.delete_notification_filter_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(InstanceNotification.objects.filter(id=self.notification_filter_to_delete_id).exists())

    def test_customer_can_delete_notification_filter(self):
        self.client.force_login(user=self.standard_user)
        request_notification_filter_test = InstanceNotification.objects.create(name="request_test_filter_4",
                                                                               profile=self.standard_user.profile)
        self.kwargs["pk"] = request_notification_filter_test.id

        response = self.client.delete(self.delete_notification_filter_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_cannot_delete_notification_filter_when_logout(self):
        self.client.logout()
        response = self.client.delete(self.delete_notification_filter_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
