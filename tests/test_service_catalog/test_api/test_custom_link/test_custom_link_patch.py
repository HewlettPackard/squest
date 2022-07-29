from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.test_views.test_admin.test_tools.test_custom_links.base_test_custom_link import \
    BaseTestCustomLink
from tests.utils import check_data_in_dict


class TestApiCustomLinkPatch(BaseTestCustomLink):

    def setUp(self):
        super(TestApiCustomLinkPatch,self).setUp()
        self.kwargs = {
            'pk': self.test_custom_link.id
        }
        self.get_custom_link_details_url = reverse('api_custom_link_details', kwargs=self.kwargs)
        self.patch_data = {
            'name': "new_name",
            'url': "new_url",
        }
        self.expected_data = {
            'id': self.test_custom_link.id,
            'name': "new_name",
            'text': self.test_custom_link.text,
            'url': "new_url",
            'button_class': self.test_custom_link.button_class,
            'when': self.test_custom_link.when,
            'is_admin_only': self.test_custom_link.is_admin_only,
            'enabled': self.test_custom_link.enabled,
            'loop': self.test_custom_link.loop,
            'services': [self.service_test.id]
        }

    def test_admin_patch_operation(self):
        response = self.client.patch(self.get_custom_link_details_url, data=self.patch_data,
                                     content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        check_data_in_dict(self, [self.expected_data], [response.data])

    def test_customer_cannot_patch_operation(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.patch(self.get_custom_link_details_url, data=self.patch_data,
                                     content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_patch_operation_when_logout(self):
        self.client.logout()
        response = self.client.patch(self.get_custom_link_details_url, data=self.patch_data,
                                     content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
