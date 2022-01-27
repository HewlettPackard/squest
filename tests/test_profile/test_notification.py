from django.urls import reverse
from tests.test_service_catalog.base import BaseTest


class TestNotification(BaseTest):

    def setUp(self):
        super(TestNotification, self).setUp()
        self.add_service_url = reverse('profiles:notification_add_service')
        self.switch_notif_url = reverse('profiles:notification_switch')

    def test_notification_switch(self):
        # by default notification are enabled
        self.assertTrue(self.superuser.profile.notification_enabled)
        # switch to disabled
        response = self.client.get(self.switch_notif_url)
        self.assertEqual(302, response.status_code)
        self.superuser.refresh_from_db()
        self.assertFalse(self.superuser.profile.notification_enabled)
        # switch back to enabled
        response = self.client.get(self.switch_notif_url)
        self.assertEqual(302, response.status_code)
        self.superuser.refresh_from_db()
        self.assertTrue(self.superuser.profile.notification_enabled)

    def test_notification_add_service(self):
        response = self.client.get(self.add_service_url)
        self.assertEqual(200, response.status_code)

        data = {
            "service": [self.service_test.id]
        }
        self.assertNotIn(self.service_test, self.superuser.profile.subscribed_services_notification.all())
        response = self.client.post(self.add_service_url, data=data)
        self.assertEqual(302, response.status_code)
        self.superuser.refresh_from_db()
        self.assertIn(self.service_test, self.superuser.profile.subscribed_services_notification.all())

    def test_notification_keep_service(self):
        self.superuser.profile.subscribed_services_notification.add(self.service_test)
        data = {
            "service": [self.service_test.id]
        }
        response = self.client.post(self.add_service_url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertIn(self.service_test, self.superuser.profile.subscribed_services_notification.all())

    def test_notification_add_2_time_service(self):
        data = {
            "service": [self.service_test.id, self.service_test.id]
        }
        response = self.client.post(self.add_service_url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertIn(self.service_test, self.superuser.profile.subscribed_services_notification.all())

    def test_notification_change_service(self):
        self.superuser.profile.subscribed_services_notification.add(self.service_test)
        data = {"service": [self.service_test_2.id]}
        response = self.client.post(self.add_service_url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertNotIn(self.service_test, self.superuser.profile.subscribed_services_notification.all())
        self.assertIn(self.service_test_2, self.superuser.profile.subscribed_services_notification.all())

    def test_notification_add_another_service(self):
        self.superuser.profile.subscribed_services_notification.add(self.service_test)
        data = {
            "service": [self.service_test_2.id]
        }
        data["service"].append(self.service_test.id)
        response = self.client.post(self.add_service_url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertIn(self.service_test, self.superuser.profile.subscribed_services_notification.all())
        self.assertIn(self.service_test_2, self.superuser.profile.subscribed_services_notification.all())

    def test_notification_add_several_service(self):
        data = {
            "service": [self.service_test.id, self.service_test_2.id]
        }
        response = self.client.post(self.add_service_url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertIn(self.service_test, self.superuser.profile.subscribed_services_notification.all())
        self.assertIn(self.service_test_2, self.superuser.profile.subscribed_services_notification.all())

    def test_notification_cannot_add_non_existing_service(self):
        data = {
            "service": 999999
        }
        response = self.client.post(self.add_service_url, data=data)
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
