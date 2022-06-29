from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import Portfolio
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestApiPortfolioDelete(BaseTestRequest):

    def _delete_portfolio(self, portfolio, post_status=status.HTTP_204_NO_CONTENT):
        url = reverse('api_portfolio_details', kwargs={'pk': portfolio.id})
        parent_portfolio = portfolio.parent_portfolio
        portfolio_list = portfolio.portfolio_list
        portfolio_list_count = portfolio.portfolio_list.count()
        service_list = portfolio.service_list
        expected_count = Portfolio.objects.filter(parent_portfolio=parent_portfolio).count()
        response = self.client.delete(url)
        self.assertEqual(post_status, response.status_code)
        if post_status == status.HTTP_204_NO_CONTENT:
            expected_count += portfolio_list_count - 1
            for children_portfolio in portfolio_list.all():
                self.assertEqual(children_portfolio.parent_portfolio, parent_portfolio)
            for children_service in service_list.all():
                self.assertEqual(children_service.parent_portfolio, parent_portfolio)
        self.assertEqual(expected_count, Portfolio.objects.filter(parent_portfolio=parent_portfolio).count())

    def test_admin_can_delete_portfolio_with_children(self):
        self._delete_portfolio(self.portfolio_test_1)

    def test_admin_can_delete_portfolio_without_children(self):
        self._delete_portfolio(self.portfolio_test_2)

    def test_customer_cannot_delete_portfolio(self):
        self.client.force_login(user=self.standard_user)
        self._delete_portfolio(self.portfolio_test_1, status.HTTP_403_FORBIDDEN)

    def test_cannot_delete_portfolio_when_logout(self):
        self.client.logout()
        self._delete_portfolio(self.portfolio_test_1, status.HTTP_403_FORBIDDEN)
