from django.utils import timezone

from service_catalog.models import Announcement, BootstrapType
from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestServiceCatalogAnnouncementPermissionsViews(BaseTestRequest, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.announcement = Announcement.objects.create(
            title='My announcement title',
            message='My announcement message',
            date_start=timezone.now() - timezone.timedelta(days=1),
            date_stop=timezone.now() + timezone.timedelta(days=1),
            created_by=self.testing_user,
            type=BootstrapType.INFO
        )

    def test_announcement_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='service_catalog:announcement_list',
                perm_str='service_catalog.list_announcement',
            ),
            TestingGetContextView(
                url='service_catalog:announcement_create',
                perm_str='service_catalog.add_announcement',
            ),
            TestingPostContextView(
                url='service_catalog:announcement_create',
                perm_str='service_catalog.add_announcement',
                data={
                    'title': 'My announcement title info',
                    'message': 'My announcement message info',
                    'date_start': timezone.now(),
                    'date_stop': timezone.now() + timezone.timedelta(days=2),
                    'type': BootstrapType.INFO
                }
            ),
            TestingGetContextView(
                url='service_catalog:announcement_edit',
                perm_str='service_catalog.change_announcement',
                url_kwargs={'pk': self.announcement.id}
            ),
            TestingPostContextView(
                url='service_catalog:announcement_edit',
                perm_str='service_catalog.change_announcement',
                url_kwargs={'pk': self.announcement.id},
                data={
                    'title': 'My announcement title danger',
                    'message': 'My announcement message danger',
                    'date_start': timezone.now(),
                    'date_stop': timezone.now() + timezone.timedelta(days=7),
                    'type': BootstrapType.DANGER
                }
            ),
            TestingGetContextView(
                url='service_catalog:announcement_delete',
                perm_str='service_catalog.delete_announcement',
                url_kwargs={'pk': self.announcement.id}
            ),
            TestingPostContextView(
                url='service_catalog:announcement_delete',
                perm_str='service_catalog.delete_announcement',
                url_kwargs={'pk': self.announcement.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)
