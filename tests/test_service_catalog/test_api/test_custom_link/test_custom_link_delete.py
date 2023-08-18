from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import  CustomLink
from tests.test_service_catalog.test_views.test_admin.test_tools.test_custom_links.base_test_custom_link import \
    BaseTestCustomLinkAPI


class TestApiCustomLinkDelete(BaseTestCustomLinkAPI):

    def setUp(self):
        super(TestApiCustomLinkDelete, self).setUp()
        self.kwargs = {
            'pk': self.test_custom_link.id
        }
        self.get_custom_link_details_url = reverse('api_customlink_details', kwargs=self.kwargs)
        self.custom_link_to_delete_id = self.update_operation_test.id

    def test_admin_delete_custom_link(self):
        custom_link_count = CustomLink.objects.count()
        response = self.client.delete(self.get_custom_link_details_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(custom_link_count - 1, CustomLink.objects.count())
        self.assertFalse(CustomLink.objects.filter(id=self.custom_link_to_delete_id).exists())

    def test_customer_cannot_delete_custom_link(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.delete(self.get_custom_link_details_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_delete_custom_link_when_logout(self):
        self.client.logout()
        response = self.client.delete(self.get_custom_link_details_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
