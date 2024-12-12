from profiles.models.squest_permission import Permission

from tests.test_profiles.base.base_test_profile import BaseTestProfile
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestProfilesGlobalScopePermissionsViews(BaseTestProfile, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.global_scope.add_user_in_role(self.standard_user, self.empty_role)

    def test_globalscope(self):
        testing_view_list = [
            TestingGetContextView(
                url='profiles:globalscope_rbac',
                perm_str_list=['profiles.view_users_globalscope'],
            ),
            TestingGetContextView(
                url='profiles:globalscope_default_permissions',
                perm_str_list=['profiles.view_globalscope'],
            ),
            TestingGetContextView(
                url='profiles:globalscope_edit',
                perm_str_list=['profiles.change_globalscope'],
            ),
            TestingPostContextView(
                url='profiles:globalscope_edit',
                perm_str_list=['profiles.change_globalscope'],
                data={'user_permission': [
                    Permission.objects.filter(content_type__app_label='service_catalog').first().id]}
            ),
            TestingGetContextView(
                url='profiles:globalscope_rbac_create',
                perm_str_list=['profiles.add_users_globalscope'],
                url_kwargs={'scope_id': self.global_scope.id}
            ),
            TestingPostContextView(
                url='profiles:globalscope_rbac_create',
                perm_str_list=['profiles.add_users_globalscope'],
                url_kwargs={'scope_id': self.global_scope.id},
                data={'users': self.standard_user.id, 'roles': self.empty_role.id}
            ),
            TestingPostContextView(
                url='profiles:globalscope_rbac_delete',
                perm_str_list=['profiles.delete_users_globalscope'],
                url_kwargs={
                    'pk': self.global_scope.id,
                    'user_id': self.standard_user.id,
                    'role_id': self.empty_role.id
                },
            ),
            TestingGetContextView(
                url='profiles:globalscope_rbac_delete',
                perm_str_list=['profiles.delete_users_globalscope'],
                url_kwargs={
                    'pk': self.global_scope.id,
                    'user_id': self.testing_user.id,
                },
            ),
            TestingPostContextView(
                url='profiles:globalscope_rbac_delete',
                perm_str_list=['profiles.delete_users_globalscope'],
                url_kwargs={
                    'pk': self.global_scope.id,
                    'user_id': self.testing_user.id,
                },
            )
        ]
        self.run_permissions_tests(testing_view_list)