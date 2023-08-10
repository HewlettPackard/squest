from tests.test_profiles.base.base_test_profile import BaseTestProfile
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestProfilesQuotaPermissionsViews(BaseTestProfile, TestPermissionEndpoint):
    def test_quota_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='profiles:quota_list',
                perm_str='profiles.list_quota'
            ),
            TestingGetContextView(
                url='profiles:quota_details',
                perm_str='profiles.view_quota',
                url_kwargs={'pk': self.test_quota_org.id}
            ),
            TestingGetContextView(
                url='profiles:organization_quota_edit',
                perm_str='profiles.change_quota',
                url_kwargs={'scope_id': self.test_org.id}
            ),
            TestingPostContextView(
                url='profiles:organization_quota_edit',
                perm_str='profiles.change_quota',
                url_kwargs={'scope_id': self.test_org.id},
                data={
                    f"attribute_definition_{self.cpu_attribute.id}": 100,
                    f"attribute_definition_{self.other_attribute.id}": 50
                }
            ),
            TestingGetContextView(
                url='profiles:team_quota_edit',
                perm_str='profiles.change_quota',
                url_kwargs={'scope_id': self.test_quota_scope_team.id}
            ),
            TestingPostContextView(
                url='profiles:team_quota_edit',
                perm_str='profiles.change_quota',
                url_kwargs={'scope_id': self.test_quota_scope_team.id},
                data={
                    f"attribute_definition_{self.cpu_attribute.id}": 100,
                    f"attribute_definition_{self.other_attribute.id}": 50
                }
            ),
            TestingGetContextView(
                url='profiles:quota_delete',
                perm_str='profiles.delete_quota',
                url_kwargs={'pk': self.test_quota_org.id}
            ),
            TestingPostContextView(
                url='profiles:quota_delete',
                perm_str='profiles.delete_quota',
                url_kwargs={'pk': self.test_quota_org.id}
            ),
        ]
        self.run_permissions_tests(testing_view_list)
