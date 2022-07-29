from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.test_views.test_admin.test_tools.test_custom_links.base_test_custom_link import \
    BaseTestCustomLink
from tests.utils import check_data_in_dict


class TestApiCustomLinkDetails(BaseTestCustomLink):

    def setUp(self):
        super(TestApiCustomLinkDetails, self).setUp()
        self.kwargs = {
            'pk': self.test_custom_link.id
        }
        self.get_custom_link_details_url = reverse('api_custom_link_details', kwargs=self.kwargs)
        self.expected_data = {
            'id': self.test_custom_link.id,
            'name': self.test_custom_link.name,
            'text': self.test_custom_link.text,
            'url': self.test_custom_link.url,
            'button_class': self.test_custom_link.button_class,
            'when': self.test_custom_link.when,
            'is_admin_only': self.test_custom_link.is_admin_only,
            'enabled': self.test_custom_link.enabled,
            'loop': self.test_custom_link.loop,
            'services': [self.service_test.id]
        }
        self.expected_data_list = [self.expected_data]

    def test_admin_get_custom_link_detail(self):
        response = self.client.get(self.get_custom_link_details_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data_list = [response.data]
        check_data_in_dict(self, self.expected_data_list, data_list)

    def test_customer_get_custom_link_detail(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.get_custom_link_details_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_get_custom_link_details_when_logout(self):
        self.client.logout()
        response = self.client.get(self.get_custom_link_details_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
