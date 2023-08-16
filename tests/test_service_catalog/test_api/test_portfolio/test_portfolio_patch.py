from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequestAPI
from tests.utils import check_data_in_dict


class TestApiPortfolioPatch(BaseTestRequestAPI):

    def setUp(self):
        super(TestApiPortfolioPatch, self).setUp()
        self.patch_data = {
            'parent_portfolio': None,
        }
        self.kwargs = {
            'pk': self.portfolio_test_2.id
        }
        self.get_portfolio_details_url = reverse('api_portfolio_details', kwargs=self.kwargs)
        self.expected_data = {
            'id': self.portfolio_test_2.id,
            'name': self.portfolio_test_2.name,
            'image': None,
            'parent_portfolio': self.patch_data['parent_portfolio'],
            'portfolio_list': [portfolio.id for portfolio in self.portfolio_test_2.portfolio_list.all()],
            'service_list': [service.id for service in self.portfolio_test_2.service_list.all()]
        }

    def test_admin_can_patch_portfolio(self):
        response = self.client.patch(self.get_portfolio_details_url, data=self.patch_data,
                                     format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        check_data_in_dict(self, [self.expected_data], [response.data])

    def test_customer_cannot_patch_portfolio(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.patch(self.get_portfolio_details_url, data=self.patch_data,
                                     format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_patch_portfolio_when_logout(self):
        self.client.logout()
        response = self.client.patch(self.get_portfolio_details_url, data=self.patch_data,
                                     format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
