from profiles.models import InstanceNotification
from tests.test_profiles.base.base_test_profile import BaseTestProfile


class BaseTestInstanceNotification(BaseTestProfile):

    def setUp(self):
        super(BaseTestInstanceNotification, self).setUp()



        self.support_notification_filter_test = InstanceNotification.objects.create(name="support_test_filter",
                                                                                    profile=self.superuser.profile)
        self.support_notification_filter_test_2 = InstanceNotification.objects.create(name="support_test_filter_2",
                                                                                      profile=self.superuser.profile)
        self.support_notification_filter_test_3 = InstanceNotification.objects.create(name="support_test_filter_3",
                                                                                      profile=self.superuser_2.profile)
