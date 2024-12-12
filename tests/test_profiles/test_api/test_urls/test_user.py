from tests.permission_endpoint import TestPermissionEndpoint, TestingGetContextView, TestingPostContextView
from tests.test_profiles.base.base_test_profile import BaseTestProfileAPI


class TestProfilesUserPermissionsEndpoint(BaseTestProfileAPI, TestPermissionEndpoint):
    def test_user_views(self):
        testing_view_list = [
            # TODO: to be tested when User has been replaced by SquestUser (list_user permission not defined)
            # TestingGetUIViews(
            #     url='profiles:api_user_list_create',
            #     perm_str_list=['auth.list_user'],
            # ),
            TestingGetContextView(
                url='api_user_details',
                perm_str_list=['auth.view_user'],
                url_kwargs={'pk': self.standard_user.id}
            ),
            TestingPostContextView(
                url='api_user_list_create',
                perm_str_list=['auth.add_user'],
                data={
                    'username': "testuser",
                    'password': "password",
                },
            )
        ]
        self.run_permissions_tests(testing_view_list)