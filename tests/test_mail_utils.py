from service_catalog.mail_utils import _get_admin_emails
from tests.test_service_catalog.base import BaseTest


class TestMailUtils(BaseTest):

    def setUp(self):
        super(TestMailUtils, self).setUp()

    def test_get_admin_emails(self):
        # Test 1 - admin disabled notification
        self.superuser.profile.notification_enabled = False
        self.superuser.save()
        self.assertEquals(0, len(_get_admin_emails(service=self.service_test)))

        # Test 2 - admin enabled notification but no service subscribed
        self.superuser.profile.notification_enabled = True
        self.superuser.save()
        self.assertEquals(0, len(_get_admin_emails(service=self.service_test)))

        # Test 3 - admin enabled notification and service subscribed
        self.superuser.profile.notification_enabled = True
        self.superuser.profile.subscribed_services_notification.add(self.service_test)
        self.superuser.save()
        self.assertEquals(1, len(_get_admin_emails(service=self.service_test)))
