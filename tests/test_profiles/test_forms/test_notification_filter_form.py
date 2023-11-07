from profiles.forms import InstanceNotificationForm, RequestNotificationForm
from tests.test_profiles.base.base_test_profile import BaseTestProfile


class TestNotificationForm(BaseTestProfile):

    def test_m2m_saved(self):
        data = {
            "name": "test_notification_form",
            "services": [self.service_test]
        }
        form = InstanceNotificationForm(user=self.standard_user, data=data)
        form.is_valid()
        saved_filter = form.save()
        self.assertIn(self.service_test, saved_filter.services.all())

        form = RequestNotificationForm(user=self.standard_user, data=data)
        form.is_valid()
        saved_filter = form.save()
        self.assertIn(self.service_test, saved_filter.services.all())
