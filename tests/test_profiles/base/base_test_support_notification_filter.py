from django.test import TestCase
from rest_framework.test import APITestCase

from profiles.models import InstanceNotification
from tests.test_profiles.base.base_test_profile import BaseTestProfileCommon


class BaseTestInstanceNotificationCommon(BaseTestProfileCommon):

    def setUp(self):
        super(BaseTestInstanceNotificationCommon, self).setUp()

        self.support_notification_filter_test = InstanceNotification.objects.create(name="support_test_filter",
                                                                                    profile=self.superuser.profile)
        self.support_notification_filter_test_2 = InstanceNotification.objects.create(name="support_test_filter_2",
                                                                                      profile=self.superuser.profile)
        self.support_notification_filter_test_3 = InstanceNotification.objects.create(name="support_test_filter_3",
                                                                                      profile=self.superuser_2.profile)


class BaseTestInstanceNotification(TestCase, BaseTestInstanceNotificationCommon):
    pass


class BaseTestInstanceNotificationAPI(APITestCase, BaseTestInstanceNotificationCommon):
    pass
