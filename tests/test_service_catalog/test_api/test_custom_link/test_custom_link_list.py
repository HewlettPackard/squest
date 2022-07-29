from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import CustomLink
from tests.test_service_catalog.test_views.test_admin.test_tools.test_custom_links.base_test_custom_link import \
    BaseTestCustomLink


class TestApiCustomLinkList(BaseTestCustomLink):

    def setUp(self):
        super(TestApiCustomLinkList, self).setUp()
        self.get_custom_link_list_url = reverse('api_custom_link_list_create')

    def test_get_all_custom_link(self):
        response = self.client.get(self.get_custom_link_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], CustomLink.objects.count())

    def test_customer_all_custom_link(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.get_custom_link_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_get_operation_list_when_logout(self):
        self.client.logout()
        response = self.client.get(self.get_custom_link_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
