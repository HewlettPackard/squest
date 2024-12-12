from service_catalog.models import CustomLink
from tests.permission_endpoint import TestPermissionEndpoint, TestingGetContextView, TestingPostContextView, \
    TestingPatchContextView, TestingPutContextView, TestingDeleteContextView
from tests.test_service_catalog.base_test_request import BaseTestRequestAPI


class TestServiceCatalogPortfolioPermissionsEndpoint(BaseTestRequestAPI, TestPermissionEndpoint):
    def test_portfolio_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='api_portfolio_list_create',
                perm_str_list=['service_catalog.list_portfolio'],
            ),
            TestingPostContextView(
                url='api_portfolio_list_create',
                perm_str_list=['service_catalog.add_portfolio'],
                data={
                    'name': "New portfolio"
                }
            ),
            TestingGetContextView(
                url='api_portfolio_details',
                perm_str_list=['service_catalog.view_portfolio'],
                url_kwargs={'pk': self.portfolio_test_1.id}
            ),
            TestingPutContextView(
                url='api_portfolio_details',
                perm_str_list=['service_catalog.change_portfolio'],
                data={
                    'name': 'Portfolio PUT',
                },
                url_kwargs={'pk': self.portfolio_test_1.id}
            ),
            TestingPatchContextView(
                url='api_portfolio_details',
                perm_str_list=['service_catalog.change_portfolio'],
                data={
                    'name': 'Portfolio PATCH',
                },
                url_kwargs={'pk': self.portfolio_test_1.id}
            ),
            TestingDeleteContextView(
                url='api_portfolio_details',
                perm_str_list=['service_catalog.delete_portfolio'],
                url_kwargs={'pk': self.portfolio_test_1.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)