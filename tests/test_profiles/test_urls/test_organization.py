from profiles.models import Organization
from tests.test_profiles.base.base_test_profile import BaseTestProfile
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestProfilesOrganizationPermissionsViews(BaseTestProfile, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.test_quota_scope_org.add_user_in_role(self.standard_user, self.empty_role)
        # organization delete is protected when organization have instances
        self.organization_to_delete = Organization.objects.create(name="To delete")

    def test_organization_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='profiles:organization_list',
                perm_str='profiles.list_organization',
            ),
            TestingGetContextView(
                url='profiles:organization_create',
                perm_str='profiles.add_organization',
            ),
            TestingPostContextView(
                url='profiles:organization_create',
                perm_str='profiles.add_organization',
                data={
                    'name': 'New organization',
                    'description': 'The description',
                    'roles': []
                }
            ),
            TestingGetContextView(
                url='profiles:organization_details',
                perm_str='profiles.view_organization',
                url_kwargs={'pk': self.test_quota_scope_org.id}
            ),
            TestingGetContextView(
                url='profiles:organization_edit',
                perm_str='profiles.change_organization',
                url_kwargs={'pk': self.test_quota_scope_org.id}
            ),
            TestingPostContextView(
                url='profiles:organization_edit',
                perm_str='profiles.change_organization',
                url_kwargs={'pk': self.test_quota_scope_org.id},
                data={
                    'name': 'Organization updated',
                    'description': 'The description updated',
                    'roles': []
                }
            ),
            TestingGetContextView(
                url='profiles:organization_rbac_create',
                perm_str='profiles.add_users_organization',
                url_kwargs={'scope_id': self.test_quota_scope_org.id}
            ),
            TestingPostContextView(
                url='profiles:organization_rbac_create',
                perm_str='profiles.add_users_organization',
                url_kwargs={'scope_id': self.test_quota_scope_org.id},
                data={'users': self.standard_user.id, 'roles': self.empty_role.id}
            ),
            TestingPostContextView(
                url='profiles:organization_rbac_delete',
                perm_str='profiles.delete_users_organization',
                url_kwargs={
                    'pk': self.test_quota_scope_org.id,
                    'user_id': self.standard_user.id,
                    'role_id': self.team_member_role.id
                },
            ),
            TestingGetContextView(
                url='profiles:organization_rbac_delete',
                perm_str='profiles.delete_users_organization',
                url_kwargs={
                    'pk': self.test_quota_scope_org.id,
                    'user_id': self.standard_user.id,
                },
            ),
            TestingPostContextView(
                url='profiles:organization_rbac_delete',
                perm_str='profiles.delete_users_organization',
                url_kwargs={
                    'pk': self.test_quota_scope_org.id,
                    'user_id': self.standard_user.id,
                },
            ),
            TestingGetContextView(
                url='profiles:organization_delete',
                perm_str='profiles.delete_organization',
                url_kwargs={'pk': self.organization_to_delete.id}
            ),
            TestingPostContextView(
                url='profiles:organization_delete',
                perm_str='profiles.delete_organization',
                url_kwargs={'pk': self.organization_to_delete.id},
            )
        ]
        self.run_permissions_tests(testing_view_list)
