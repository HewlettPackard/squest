from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestServiceCatalogPortfolioPermissionsViews(BaseTestRequest, TestPermissionEndpoint):
    def test_portfolio_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='service_catalog:portfolio_list',
                perm_str='service_catalog.list_portfolio',
            ),
            TestingGetContextView(
                url='service_catalog:portfolio_create',
                perm_str='service_catalog.add_portfolio',
            ),
            TestingPostContextView(
                url='service_catalog:portfolio_create',
                perm_str='service_catalog.add_portfolio',
                data={
                    'name': 'New name'
                }
            ),
            TestingGetContextView(
                url='service_catalog:portfolio_edit',
                perm_str='service_catalog.change_portfolio',
                url_kwargs={'pk': self.portfolio_test_1.id}
            ),
            TestingPostContextView(
                url='service_catalog:portfolio_edit',
                perm_str='service_catalog.change_portfolio',
                url_kwargs={'pk': self.portfolio_test_1.id},
                data={
                    'name': 'name updated'
                }
            ),
            TestingGetContextView(
                url='service_catalog:portfolio_delete',
                perm_str='service_catalog.delete_portfolio',
                url_kwargs={'pk': self.portfolio_test_1.id}
            ),
            TestingPostContextView(
                url='service_catalog:portfolio_delete',
                perm_str='service_catalog.delete_portfolio',
                url_kwargs={'pk': self.portfolio_test_1.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)
