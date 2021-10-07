from django.utils import timezone

from service_catalog.filters.announcement_filter import AnnouncementFilter
from service_catalog.models import BootstrapType, Announcement
from tests.test_service_catalog.base import BaseTest


class TestAnnouncementFilter(BaseTest):

    def test_get_opens(self):
        Announcement.objects.create(
            title='My announcement past',
            message='My announcement past',
            date_start=timezone.now() - timezone.timedelta(days=15),
            date_stop=timezone.now() - timezone.timedelta(days=7),
            created_by=self.superuser,
            type=BootstrapType.INFO
        )
        Announcement.objects.create(
            title='My announcement present',
            message='My announcement present',
            date_start=timezone.now() - timezone.timedelta(days=1),
            date_stop=timezone.now() + timezone.timedelta(days=2),
            created_by=self.superuser,
            type=BootstrapType.SUCCESS
        )
        Announcement.objects.create(
            title='My announcement future',
            message='My announcement future',
            date_start=timezone.now() + timezone.timedelta(days=12),
            date_stop=timezone.now() + timezone.timedelta(days=20),
            created_by=self.superuser,
            type=BootstrapType.DANGER
        )
        announcement_filter = AnnouncementFilter(data={'opens': True})
        self.assertTrue(announcement_filter.form.is_valid())
        self.assertEqual(1, announcement_filter.qs.count())
        announcement_filter = AnnouncementFilter(data={'opens': False})
        self.assertTrue(announcement_filter.form.is_valid())
        self.assertEqual(3, announcement_filter.qs.count())

