from django.urls import reverse

from service_catalog.forms.form_utils import FormUtils
from service_catalog.models import Portfolio
from tests.test_service_catalog.base import BaseTest


class PortfolioCreateTestCase(BaseTest):

    def setUp(self):
        super(PortfolioCreateTestCase, self).setUp()
        self.data = {'name': 'new portfolio',
                     "permission": FormUtils.get_default_permission_for_operation(),}

    def _create_portfolio(self, data=None, parent_portfolio=None, get_status=200, post_status=302):
        data = data if data else self.data
        url = reverse('service_catalog:portfolio_create')
        response = self.client.get(url)
        self.assertEqual(get_status, response.status_code)
        old_count = Portfolio.objects.filter(parent_portfolio__id=parent_portfolio).count()
        response = self.client.post(url, data=data)
        self.assertEqual(post_status, response.status_code)
        expected_count = old_count + 1 if get_status == 200 and post_status == 302 else old_count
        self.assertEqual(expected_count, Portfolio.objects.filter(parent_portfolio__id=parent_portfolio).count())

    def test_admin_can_create_a_portfolio_in_root(self):
        self._create_portfolio()

    def test_customer_cannot_create_portfolio(self):
        self.client.force_login(self.standard_user)
        self._create_portfolio(get_status=403, post_status=403)

    def test_cannot_create_portfolio_when_logout(self):
        self.client.logout()
        self._create_portfolio(get_status=302, post_status=302)