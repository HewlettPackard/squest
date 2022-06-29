from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.utils import check_data_in_dict


class TestApiPortfolioDetails(BaseTestRequest):

    def setUp(self):
        super(TestApiPortfolioDetails, self).setUp()
        self.kwargs = {
            'pk': self.portfolio_test_1.id
        }
        self.get_portfolio_details_url = reverse('api_portfolio_details', kwargs=self.kwargs)
        self.expected_data = {
            'id': self.portfolio_test_1.id,
            'name': self.portfolio_test_1.name,
            'image': f"http://testserver{self.portfolio_test_1.image.url}",
            'parent_portfolio': self.portfolio_test_1.parent_portfolio,
            'portfolio_list': [portfolio.id for portfolio in self.portfolio_test_1.portfolio_list.all()],
            'service_list': [service.id for service in self.portfolio_test_1.service_list.all()]
        }
        self.expected_data_list = [self.expected_data]
        self.portfolio_test_2.enabled = False
        self.portfolio_test_2.save()

    def test_admin_can_get_portfolio_detail(self):
        response = self.client.get(self.get_portfolio_details_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data_list = [response.data]
        check_data_in_dict(self, self.expected_data_list, data_list)

    def test_customer_can_get_portfolio_detail(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.get_portfolio_details_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data_list = [response.data]
        check_data_in_dict(self, self.expected_data_list, data_list)

    def test_cannot_get_portfolio_details_when_logout(self):
        self.client.logout()
        response = self.client.get(self.get_portfolio_details_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
