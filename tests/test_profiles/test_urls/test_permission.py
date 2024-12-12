from profiles.models.squest_permission import Permission

from tests.test_profiles.base.base_test_profile import BaseTestProfile
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestProfilesPermissionPermissionsViews(BaseTestProfile, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.permission_test = Permission.objects.filter(content_type__app_label='service_catalog').first()

    def test_permission_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='profiles:permission_list',
                perm_str_list=['profiles.list_permission'],
            ),
            TestingGetContextView(
                url='profiles:permission_create',
                perm_str_list=['profiles.add_permission'],
            ),
            TestingPostContextView(
                url='profiles:permission_create',
                perm_str_list=['profiles.add_permission'],
                data={
                    'name': 'New permission',
                    'codename': 'the_code_name',
                    'content_type': self.permission_test.content_type.id
                }
            ),
            TestingGetContextView(
                url='profiles:permission_edit',
                perm_str_list=['profiles.change_permission'],
                url_kwargs={'pk': self.permission_test.id}
            ),
            TestingPostContextView(
                url='profiles:permission_edit',
                perm_str_list=['profiles.change_permission'],
                url_kwargs={'pk': self.permission_test.id},
                data={
                    'name': 'Permission updated',
                    'codename': 'the_code_name_updated',
                    'content_type': self.permission_test.content_type.id
                }
            ),
            TestingGetContextView(
                url='profiles:permission_delete',
                perm_str_list=['profiles.delete_permission'],
                url_kwargs={'pk': self.permission_test.id}
            ),
            TestingPostContextView(
                url='profiles:permission_delete',
                perm_str_list=['profiles.delete_permission'],
                url_kwargs={'pk': self.permission_test.id},

            )
        ]
        self.run_permissions_tests(testing_view_list)