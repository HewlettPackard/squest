from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import Portfolio
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestApiPortfolioList(BaseTestRequest):

    def _list_portfolio(self, parent=None, get_status=status.HTTP_200_OK):
        param_str = f"?parent_portfolio={parent.id if parent else ''}"
        response = self.client.get(reverse('api_portfolio_list_create') + param_str)
        self.assertEqual(response.status_code, get_status)
        if get_status == status.HTTP_200_OK:
            self.assertEqual(response.data['count'], parent.portfolio_list.count() if parent else Portfolio.objects.count())

    def test_admin_can_get_all_portfolio_list(self):
        self._list_portfolio()

    def test_admin_can_get_portfolio_list_of_portfolios(self):
        self._list_portfolio(self.portfolio_test_1)

    def test_customer_can_get_all_portfolio_list(self):
        self.client.force_login(user=self.standard_user)
        self._list_portfolio()

    def test_customer_can_get_portfolio_list_of_portfolios(self):
        self.client.force_login(user=self.standard_user)
        self._list_portfolio(self.portfolio_test_1)

    def test_cannot_get_portfolio_list_when_logout(self):
        self.client.logout()
        self._list_portfolio(get_status=status.HTTP_403_FORBIDDEN)
