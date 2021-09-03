from django.utils import timezone

from service_catalog.forms import AnnouncementForm
from service_catalog.models import BootstrapType
from tests.base import BaseTest


class TestAnnouncementForm(BaseTest):

    def setUp(self):
        super(TestAnnouncementForm, self).setUp()

    def test_create_announcement(self):
        data = {
            'title': 'My announcement title info',
            'message': 'My announcement message info',
            'date_start': timezone.now(),
            'date_stop': timezone.now() + timezone.timedelta(days=2),
            'type': BootstrapType.INFO
        }
        form = AnnouncementForm(data)
        self.assertTrue(form.is_valid)

    def test_create_announcement_with_stop_before_start(self):
        data = {
            'title': 'My announcement title info',
            'message': 'My announcement message info',
            'date_start': timezone.now() + timezone.timedelta(days=2),
            'date_stop': timezone.now(),
            'type': BootstrapType.INFO
        }
        form = AnnouncementForm(data)
        self.assertFalse(form.is_valid())

    def test_create_announcement_with_start_in_the_past(self):
        data = {
            'title': 'My announcement title info',
            'message': 'My announcement message info',
            'date_start': timezone.now() - timezone.timedelta(days=3),
            'date_stop': timezone.now() + timezone.timedelta(days=2),
            'type': BootstrapType.INFO
        }
        form = AnnouncementForm(data)
        self.assertFalse(form.is_valid())
