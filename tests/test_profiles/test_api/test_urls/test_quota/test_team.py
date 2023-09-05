from profiles.models import Quota
from resource_tracker_v2.models import AttributeDefinition
from tests.permission_endpoint import TestPermissionEndpoint, TestingGetContextView, TestingPostContextView, \
    TestingPatchContextView, TestingPutContextView, TestingDeleteContextView
from tests.test_profiles.base.base_test_profile import BaseTestProfileAPI


class TestProfilesQuotaTeamPermissionsEndpoint(BaseTestProfileAPI, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()

        self.attribute_test = AttributeDefinition.objects.create(name="AttributeTest")
        Quota.objects.create(scope=self.test_quota_scope_team.org, limit=99999,
                             attribute_definition=self.attribute_test)

    def test_quota_team_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='api_quota_list_create',
                perm_str='profiles.list_quota',
            ),
            TestingPostContextView(
                url='api_quota_list_create',
                perm_str='profiles.add_quota',
                data={
                    'scope': self.test_quota_scope_team.id,
                    'attribute_definition': self.attribute_test.id,
                    'limit': 500
                }
            ),
            TestingGetContextView(
                url='api_quota_details',
                perm_str='profiles.view_quota',
                url_kwargs={'pk': self.test_quota_team.id}
            ),
            TestingPutContextView(
                url='api_quota_details',
                perm_str='profiles.change_team_quota',
                data={
                    'scope': self.test_quota_team.scope.id,
                    'attribute_definition': self.cpu_attribute.id,
                    'limit': 150
                },
                url_kwargs={'pk': self.test_quota_team.id}
            ),
            TestingPatchContextView(
                url='api_quota_details',
                perm_str='profiles.change_team_quota',
                data={
                    'limit': 50
                },
                url_kwargs={'pk': self.test_quota_team.id}
            ),
            TestingDeleteContextView(
                url='api_quota_details',
                perm_str='profiles.delete_quota',
                url_kwargs={'pk': self.test_quota_team.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)
