import datetime
from unittest.mock import patch

from django.utils import timezone

from service_catalog.models import BootstrapType, Announcement
from tests.test_service_catalog.base import BaseTest


class TestAnnouncements(BaseTest):

    def setUp(self):
        super(TestAnnouncements, self).setUp()
        self.my_announcement = Announcement.objects.create(
            title='My announcement title',
            message='My announcement message',
            date_start=timezone.now(),
            date_stop=timezone.now() + timezone.timedelta(days=2),
            created_by=self.superuser,
            type=BootstrapType.SUCCESS
        )
        self.my_announcement_past = Announcement.objects.create(
            title='My announcement title past',
            message='My announcement message past',
            date_start=timezone.now() - timezone.timedelta(days=5),
            date_stop=timezone.now() - timezone.timedelta(days=1),
            created_by=self.superuser,
            type=BootstrapType.DANGER
        )
        self.my_announcement_future = Announcement.objects.create(
            title='My announcement title future',
            message='My announcement message future',
            date_start=timezone.now() + timezone.timedelta(hours=3),
            date_stop=timezone.now() + timezone.timedelta(days=2),
            created_by=self.superuser,
            type=BootstrapType.INFO
        )
        self.expected_now = 1
        self.expected_future = 2
        self.expected_past = 1

    def test_mock_announcements_in_dashboard(self):
        now_origin = timezone.now()
        future_origin = now_origin + timezone.timedelta(hours=6)
        past_origin = now_origin - timezone.timedelta(days=3)
        available_origin_now = Announcement.objects.filter(date_start__lte=now_origin).filter(date_stop__gte=now_origin)
        available_origin_future = Announcement.objects.filter(date_start__lte=future_origin).filter(date_stop__gte=future_origin)
        available_origin_past = Announcement.objects.filter(date_start__lte=past_origin).filter(date_stop__gte=past_origin)
        print(timezone.now())
        with patch.object(timezone, 'now', return_value=datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(minutes=30, hours=5)))) as mock_now:
            now_other = timezone.now()
            future_other = now_other + timezone.timedelta(hours=6)
            past_other = now_other - timezone.timedelta(days=3)
            available_other_now = Announcement.objects.filter(date_start__lte=now_other).filter(date_stop__gte=now_other)
            available_other_future = Announcement.objects.filter(date_start__lte=future_other).filter(date_stop__gte=future_other)
            available_other_past = Announcement.objects.filter(date_start__lte=past_other).filter(date_stop__gte=past_other)
        self.assertEqual(len(available_other_now), len(available_origin_now), self.expected_now)
        self.assertEqual(len(available_other_future), len(available_origin_future), self.expected_future)
        self.assertEqual(len(available_other_past), len(available_origin_past), self.expected_past)
