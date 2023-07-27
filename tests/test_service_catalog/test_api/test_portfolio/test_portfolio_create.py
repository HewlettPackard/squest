from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import Portfolio
from tests.test_service_catalog.base_test_request import BaseTestRequest

EXPECTED_FIELDS = ['id', 'name', 'parent_portfolio', 'image', 'portfolio_list', 'service_list']


class TestApiPortfolioCreate(BaseTestRequest):

    def setUp(self):
        super(TestApiPortfolioCreate, self).setUp()
        self.post_data = {
            'name': "New portfolio"
        }

    def _create_portfolio(self, parent_portfolio=None, post_status=status.HTTP_201_CREATED):
        if parent_portfolio:
            self.post_data['parent_portfolio'] = parent_portfolio
        url = reverse('api_portfolio_list_create')
        expected_count = Portfolio.objects.filter(parent_portfolio__id=parent_portfolio).count()
        response = self.client.post(url, data=self.post_data)
        self.assertEqual(post_status, response.status_code)
        if post_status == status.HTTP_201_CREATED:
            expected_count += 1
            for field_name in EXPECTED_FIELDS:
                self.assertIn(field_name, response.data)
        self.assertEqual(expected_count, Portfolio.objects.filter(parent_portfolio__id=parent_portfolio).count())

    def test_admin_can_post_portfolio_in_root(self):
        self._create_portfolio()

    def test_admin_can_post_portfolio_in_portfolio(self):
        self._create_portfolio(parent_portfolio=self.portfolio_test_1.id)

    def test_customer_cannot_post_portfolio(self):
        self.client.force_login(user=self.standard_user)
        self._create_portfolio(post_status=status.HTTP_403_FORBIDDEN)

    def test_cannot_post_portfolio_when_logout(self):
        self.client.logout()
        self._create_portfolio(post_status=status.HTTP_403_FORBIDDEN)
