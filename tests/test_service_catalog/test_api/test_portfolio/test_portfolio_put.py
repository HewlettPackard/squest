from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequestAPI
from tests.utils import check_data_in_dict


class TestApiPortfolioPut(BaseTestRequestAPI):

    def setUp(self):
        super(TestApiPortfolioPut, self).setUp()
        self.put_data = {
            'name': "new name",
            'parent_portfolio': None,
        }
        self.kwargs = {
            'pk': self.portfolio_test_2.id
        }
        self.get_portfolio_details_url = reverse('api_portfolio_details', kwargs=self.kwargs)

    def test_admin_can_put_portfolio(self):
        response = self.client.put(self.get_portfolio_details_url, data=self.put_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        check_data_in_dict(self, [self.put_data], [response.data])

    def test_admin_cannot_put_on_portfolio_not_full(self):
        self.put_data.pop('name')
        response = self.client.put(self.get_portfolio_details_url, data=self.put_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_customer_cannot_put_portfolio(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.put(self.get_portfolio_details_url, data=self.put_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_put_portfolio_when_logout(self):
        self.client.logout()
        response = self.client.put(self.get_portfolio_details_url, data=self.put_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
