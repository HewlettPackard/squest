from profiles.models import Organization
from tests.permission_endpoint import TestPermissionEndpoint, TestingGetContextView, TestingPostContextView, \
    TestingPatchContextView, TestingPutContextView, TestingDeleteContextView
from tests.test_profiles.base.base_test_profile import BaseTestProfileAPI


class TestProfilesOrganizationPermissionsEndpoint(BaseTestProfileAPI, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.test_quota_scope_org.add_user_in_role(self.standard_user, self.empty_role)
        # organization delete is protected when organization have instances
        self.organization_to_delete = Organization.objects.create(name="To delete")

    def test_organization_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='api_organization_list_create',
                perm_str_list=['profiles.list_organization'],
            ),
            TestingPostContextView(
                url='api_organization_list_create',
                perm_str_list=['profiles.add_organization'],
                data={
                    'name': "test organization",
                    'description': "test description"
                }
            ),
            TestingGetContextView(
                url='api_organization_details',
                perm_str_list=['profiles.view_organization'],
                url_kwargs={'pk': self.test_quota_scope_org.id}
            ),
            TestingPutContextView(
                url='api_organization_details',
                perm_str_list=['profiles.change_organization'],
                data={
                    'name': "test organization put",
                    'description': "test description put"
                },
                url_kwargs={'pk': self.test_quota_scope_org.id}
            ),
            TestingPatchContextView(
                url='api_organization_details',
                perm_str_list=['profiles.change_organization'],
                data={
                    'description': "new description patch"
                },
                url_kwargs={'pk': self.test_quota_scope_org.id}
            ),
            TestingGetContextView(
                url='api_team_rbac_create',
                perm_str_list=['profiles.view_users_organization'],
                url_kwargs={'scope_id': self.test_quota_scope_org.id}
            ),
            TestingPostContextView(
                url='api_organization_rbac_create',
                perm_str_list=['profiles.add_users_organization'],
                url_kwargs={'scope_id': self.test_quota_scope_org.id},
                data={'users': [self.standard_user.id], 'roles': [self.empty_role.id]}
            ),
            TestingDeleteContextView(
                url='api_organization_rbac_delete',
                perm_str_list=['profiles.delete_users_organization'],
                url_kwargs={
                    'scope_id': self.test_quota_scope_org.id,
                    'user_id': self.standard_user.id,
                    'role_id': self.team_member_role.id
                },
            ),
            TestingDeleteContextView(
                url='api_organization_user_delete',
                perm_str_list=['profiles.delete_users_organization'],
                url_kwargs={
                    'scope_id': self.test_quota_scope_org.id,
                    'user_id': self.standard_user.id,
                },
            ),
            TestingDeleteContextView(
                url='api_organization_details',
                perm_str_list=['profiles.delete_organization'],
                url_kwargs={'pk': self.organization_to_delete.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)