from profiles.models.squest_permission import Permission

from tests.test_profiles.base.base_test_profile import BaseTestProfile
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestProfilesGlobalPermissionPermissionsViews(BaseTestProfile, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.global_permission.add_user_in_role(self.standard_user, self.empty_role)

    def test_globalpermission(self):
        testing_view_list = [
            TestingGetContextView(
                url='profiles:globalpermission_rbac',
                perm_str='profiles.view_users_globalpermission',
            ),
            TestingGetContextView(
                url='profiles:globalpermission_default_permissions',
                perm_str='profiles.view_globalpermission',
            ),
            TestingGetContextView(
                url='profiles:globalpermission_edit',
                perm_str='profiles.change_globalpermission',
            ),
            TestingPostContextView(
                url='profiles:globalpermission_edit',
                perm_str='profiles.change_globalpermission',
                data={'user_permission': [
                    Permission.objects.filter(content_type__app_label='service_catalog').first().id]}
            ),
            TestingGetContextView(
                url='profiles:globalpermission_rbac_create',
                perm_str='profiles.add_users_globalpermission',
                url_kwargs={'scope_id': self.global_permission.id}
            ),
            TestingPostContextView(
                url='profiles:globalpermission_rbac_create',
                perm_str='profiles.add_users_globalpermission',
                url_kwargs={'scope_id': self.global_permission.id},
                data={'users': self.standard_user.id, 'roles': self.empty_role.id}
            ),
            TestingPostContextView(
                url='profiles:globalpermission_rbac_delete',
                perm_str='profiles.delete_users_globalpermission',
                url_kwargs={
                    'pk': self.global_permission.id,
                    'user_id': self.standard_user.id,
                    'role_id': self.empty_role.id
                },
            ),
            TestingGetContextView(
                url='profiles:globalpermission_rbac_delete',
                perm_str='profiles.delete_users_globalpermission',
                url_kwargs={
                    'pk': self.global_permission.id,
                    'user_id': self.testing_user.id,
                },
            ),
            TestingPostContextView(
                url='profiles:globalpermission_rbac_delete',
                perm_str='profiles.delete_users_globalpermission',
                url_kwargs={
                    'pk': self.global_permission.id,
                    'user_id': self.testing_user.id,
                },
            )
        ]
        self.run_permissions_tests(testing_view_list)
