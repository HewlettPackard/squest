from profiles.models import Permission
from tests.permission_endpoint import TestPermissionEndpoint, TestingGetContextView, TestingPostContextView, \
    TestingPatchContextView, TestingPutContextView, TestingDeleteContextView
from tests.test_profiles.base.base_test_profile import BaseTestProfileAPI


class TestProfilesPermissionPermissionsEndpoint(BaseTestProfileAPI, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.permission_test = Permission.objects.filter(content_type__app_label='service_catalog').first()

    def test_permission_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='api_permission_list_create',
                perm_str='profiles.list_permission',
            ),
            TestingPostContextView(
                url='api_permission_list_create',
                perm_str='profiles.add_permission',
                data={
                    'name': 'New permission',
                    'codename': 'the_code_name',
                    'content_type': self.permission_test.content_type.id
                }
            ),
            TestingGetContextView(
                url='api_permission_details',
                perm_str='profiles.view_permission',
                url_kwargs={'pk': self.permission_test.id}
            ),
            TestingPutContextView(
                url='api_permission_details',
                perm_str='profiles.change_permission',
                data={
                    'name': 'New permission put',
                    'codename': 'the_code_name_put',
                    'content_type': self.permission_test.content_type.id
                },
                url_kwargs={'pk': self.permission_test.id}
            ),
            TestingPatchContextView(
                url='api_permission_details',
                perm_str='profiles.change_permission',
                data={
                    'name': 'New permission patch',
                },
                url_kwargs={'pk': self.permission_test.id}
            ),
            TestingDeleteContextView(
                url='api_permission_details',
                perm_str='profiles.delete_permission',
                url_kwargs={'pk': self.permission_test.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)
