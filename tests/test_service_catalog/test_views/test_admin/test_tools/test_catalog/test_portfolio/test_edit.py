from django.urls import reverse

from service_catalog.forms.form_utils import FormUtils
from tests.test_service_catalog.base import BaseTest


class PortfolioEditTestCase(BaseTest):

    def setUp(self):
        super(PortfolioEditTestCase, self).setUp()
        self.data = {
            'name': 'updated',
            "permission": FormUtils.get_default_permission_for_operation(),
        }

    def _edit_portfolio(self, data=None, get_status=200, post_status=302):
        data = data if data else self.data
        url = reverse('service_catalog:portfolio_edit', kwargs={'pk': self.portfolio_test_1.id})
        response = self.client.get(url)
        self.assertEqual(get_status, response.status_code)
        response = self.client.post(url, data=data)
        self.assertEqual(post_status, response.status_code)
        self.portfolio_test_1.refresh_from_db()
        if get_status == 200 and post_status == 302:
            self.assertEqual("updated", self.portfolio_test_1.name)

    def test_admin_can_edit_portfolio(self):
        self._edit_portfolio()

    def test_customer_cannot_edit_portfolio(self):
        self.client.force_login(self.standard_user)
        self._edit_portfolio(get_status=403, post_status=403)

    def test_cannot_edit_portfolio_when_logout(self):
        self.client.logout()
        self._edit_portfolio(get_status=302, post_status=302)