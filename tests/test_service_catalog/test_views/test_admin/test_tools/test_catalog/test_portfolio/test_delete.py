from django.urls import reverse

from service_catalog.models import Portfolio, Service
from tests.test_service_catalog.base import BaseTest


class PortfolioDeleteTestCase(BaseTest):

    def test_delete_portfolio_with_service_and_portfolio(self):
        portfolio = Portfolio.objects.create(name="new one", parent_portfolio=self.portfolio_test_2)
        self.service_test.parent_portfolio = self.portfolio_test_2
        self.service_test.save()
        old_count = Portfolio.objects.count()
        args = {
            'pk': self.portfolio_test_2.id,
        }
        url = reverse('service_catalog:portfolio_delete', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        response = self.client.post(url)
        self.assertEqual(302, response.status_code)
        self.portfolio_test_1.refresh_from_db()
        self.assertEqual(Portfolio.objects.count(), old_count - 1)
        self.assertIn(self.service_test, self.portfolio_test_1.service_list.all())
        self.assertIn(portfolio, self.portfolio_test_1.portfolio_list.all())

    def test_delete_portfolio_with_service_and_portfolio_in_root(self):
        self.service_test.parent_portfolio = self.portfolio_test_1
        self.service_test.save()
        old_count = Portfolio.objects.count()
        args = {
            'pk': self.portfolio_test_1.id,
        }
        url = reverse('service_catalog:portfolio_delete', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        response = self.client.post(url)
        self.assertEqual(302, response.status_code)
        self.assertEqual(Portfolio.objects.count(), old_count - 1)
        self.assertIn(self.service_test, Service.objects.filter(parent_portfolio=None))
        self.assertIn(self.portfolio_test_2, Portfolio.objects.filter(parent_portfolio=None))
