from profiles.models import RequestNotification
from tests.test_profiles.base.base_test_profile import BaseTestProfile


class BaseTestRequestNotification(BaseTestProfile):

    def setUp(self):
        super(BaseTestRequestNotification, self).setUp()
        self.request_notification_filter_test = RequestNotification.objects.create(name="request_test_filter",
                                                                                   profile=self.superuser.profile)
        self.request_notification_filter_test_2 = RequestNotification.objects.create(name="request_test_filter_2",
                                                                                     profile=self.superuser.profile)
        self.request_notification_filter_test_3 = RequestNotification.objects.create(name="request_test_filter_3",
                                                                                     profile=self.superuser_2.profile)
