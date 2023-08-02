from rest_framework import status
from rest_framework.reverse import reverse_lazy

from profiles.models import RequestNotification
from tests.test_profiles.base.base_test_request_notification_filter import BaseTestRequestNotification


class TestApiRequestNotificationFilterCreate(BaseTestRequestNotification):

    def setUp(self):
        super(TestApiRequestNotificationFilterCreate, self).setUp()
        self.post_data = {
            'name': "myFilterName",
        }
        self.create_notification_filter_url = reverse_lazy('api_request_notification_filter_list_create')

    def _create_notification_filter(self):
        response = self.client.post(self.create_notification_filter_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(set(response.data.keys()),
                         {'id', 'name', 'profile', 'services', 'operations', 'request_states', 'when', 'last_updated',
                          'created'})

    def _create_notification_filter_failed(self, status_error=status.HTTP_400_BAD_REQUEST):
        response = self.client.post(self.create_notification_filter_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status_error)

    def test_admin_post_notification_filter(self):
        self._create_notification_filter()

    def test_cannot_post_notification_filter_on_another_profile(self):
        self.post_data['profile'] = self.superuser_2.profile.id
        old_count = RequestNotification.objects.filter(profile=self.superuser.profile).count()
        self._create_notification_filter()
        self.assertFalse(RequestNotification.objects.exclude(id=self.request_notification_filter_test_3.id).filter(
            profile=self.superuser_2.profile).exists())
        self.assertEqual(old_count + 1, RequestNotification.objects.filter(profile=self.superuser.profile).count())

    def test_customer_can_post_notification_filter(self):
        self.client.force_login(user=self.standard_user)
        self.post_data['profile'] = self.standard_user.profile.id
        response = self.client.post(self.create_notification_filter_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cannot_post_notification_filter_when_logout(self):
        self.client.logout()
        response = self.client.post(self.create_notification_filter_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
