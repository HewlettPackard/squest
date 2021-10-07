from django.urls import reverse
from django.utils import timezone

from service_catalog.models.bootstrap_type import BootstrapType
from service_catalog.models.announcement import Announcement
from tests.test_service_catalog.base import BaseTest


class TestAnnouncementUrls(BaseTest):

    def setUp(self):
        super(TestAnnouncementUrls, self).setUp()
        self.my_announcement = Announcement.objects.create(
            title='My announcement title',
            message='My announcement message',
            date_start=timezone.now() - timezone.timedelta(days=1),
            date_stop=timezone.now() + timezone.timedelta(days=1),
            created_by=self.superuser,
            type=BootstrapType.INFO
        )

    def test_all_get(self):
        args_announcement = {
            'announcement_id': self.my_announcement.id
        }
        urls_list = [
            reverse('service_catalog:announcement_list'),
            reverse('service_catalog:announcement_create'),
            reverse('service_catalog:announcement_edit', kwargs=args_announcement),
            reverse('service_catalog:announcement_delete', kwargs=args_announcement),
        ]
        for url in urls_list:
            response = self.client.get(url)
            self.assertEqual(200, response.status_code)
        self.client.logout()
        for url in urls_list:
            response = self.client.get(url)
            self.assertEqual(302, response.status_code)

    def test_all_delete_post(self):
        args_announcement = {
            'announcement_id': self.my_announcement.id
        }
        response = self.client.post(reverse('service_catalog:announcement_delete', kwargs=args_announcement))
        self.assertEqual(302, response.status_code)

    def test_all_post_with_data(self):
        args_announcement = {
            'announcement_id': self.my_announcement.id
        }
        test_list = [
            {'url': reverse('service_catalog:announcement_create'), 'data': {
                'title': 'My announcement title info',
                'message': 'My announcement message info',
                'date_start': timezone.now(),
                'date_stop': timezone.now() + timezone.timedelta(days=2),
                'type': BootstrapType.INFO}},
            {'url': reverse('service_catalog:announcement_edit', kwargs=args_announcement),
             'data': {
                'title': 'My announcement title danger',
                'message': 'My announcement message danger',
                'date_start': timezone.now(),
                'date_stop': timezone.now() + timezone.timedelta(days=7),
                'type': BootstrapType.DANGER}}
        ]
        announcement_count = Announcement.objects.count()
        for test in test_list:
            response = self.client.post(test['url'], data=test['data'])
            self.assertEqual(302, response.status_code)
        self.my_announcement = Announcement.objects.get(id=self.my_announcement.id)
        self.assertEqual(self.my_announcement.title, test_list[1]['data']['title'])
        self.assertEqual(self.my_announcement.message, test_list[1]['data']['message'])
        self.assertEqual(self.my_announcement.date_start, test_list[1]['data']['date_start'])
        self.assertEqual(self.my_announcement.date_stop, test_list[1]['data']['date_stop'])
        self.assertEqual(self.my_announcement.type, test_list[1]['data']['type'])
        self.assertEqual(announcement_count + 1, Announcement.objects.count())
