from django.urls import reverse
from tests.test_service_catalog.base import BaseTest


class TestNotification(BaseTest):

    def setUp(self):
        super(TestNotification, self).setUp()

    def test_notification_switch(self):
        url = reverse('profiles:notification_switch')
        # by default notification are enabled
        self.assertTrue(self.superuser.profile.notification_enabled)
        # switch to disabled
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        self.superuser.refresh_from_db()
        self.assertFalse(self.superuser.profile.notification_enabled)
        # switch back to enabled
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        self.superuser.refresh_from_db()
        self.assertTrue(self.superuser.profile.notification_enabled)

    def test_notification_add_service(self):
        url = reverse('profiles:notification_add_service')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        data = {
            "service": self.service_test.id
        }
        self.assertTrue(self.service_test not in self.superuser.profile.subscribed_services_notification.all())
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.superuser.refresh_from_db()
        self.assertTrue(self.service_test in self.superuser.profile.subscribed_services_notification.all())

        # check cannot ad the same service
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, "You have already subscribed to this service")

        # add non existing service
        data = {
            "service": 999999
        }
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, "Select a valid choice")

    def test_notification_remove_service(self):
        self.superuser.profile.subscribed_services_notification.add(self.service_test)
        self.superuser.save()
        args = {
            "service_id": self.service_test.id
        }
        url = reverse('profiles:notification_remove_service', kwargs=args)

        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        self.assertFalse(self.service_test in self.superuser.profile.subscribed_services_notification.all())

        # remove already removed service
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        self.assertFalse(self.service_test in self.superuser.profile.subscribed_services_notification.all())

        # remove non existing service
        args = {
            "service_id": 99999
        }
        url = reverse('profiles:notification_remove_service', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)
