from profiles.models import Organization, Team
from tests.test_profiles.base.base_test_profile import BaseTestProfile
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestProfilesOrganizationScopeViews(BaseTestProfile, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.organization = Organization.objects.create(name="Org1")
        self.team = Team.objects.create(name="Team", org=self.organization)


    def test_scope_redirect_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='profiles:scope_details',
                perm_str_list=['profiles.view_organization'],
                url_kwargs={'pk': self.organization.id},
                follow=True

            ),
            TestingGetContextView(
                url='profiles:scope_details',
                perm_str_list=['profiles.view_team'],
                url_kwargs={'pk': self.team.id},
                follow=True

            ),
        ]
        self.run_permissions_tests(testing_view_list)