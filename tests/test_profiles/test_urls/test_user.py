from tests.test_profiles.base.base_test_profile import BaseTestProfile
from tests.permission_endpoint import TestingGetContextView, TestPermissionEndpoint


class TestProfilesUserPermissionsViews(BaseTestProfile, TestPermissionEndpoint):
    def test_user_views(self):
        testing_view_list = [
            # TODO: to be tested when User has been replaced by SquestUser (list_user permission not defined)
            # TestingGetUIViews(
            #     url='profiles:user_list',
            #     perm_str='auth.list_user',
            # ),
            TestingGetContextView(
                url='profiles:user_details',
                perm_str='auth.view_user',
                url_kwargs={'pk': self.standard_user.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)
