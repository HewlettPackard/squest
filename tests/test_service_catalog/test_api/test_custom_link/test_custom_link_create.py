from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import CustomLink
from tests.test_service_catalog.test_views.test_admin.test_tools.test_custom_links.base_test_custom_link import \
    BaseTestCustomLinkAPI

from tests.utils import check_data_in_dict


class TestApiCustomLinkCreate(BaseTestCustomLinkAPI):

    def setUp(self):
        super(TestApiCustomLinkCreate, self).setUp()
        self.post_data = {
            'name': "new custom link",
            'text': "button_test",
            'url': "https://server.domain",

        }
        self.get_custom_link_create_url = reverse('api_customlink_list_create')

    def test_admin_post_custom_link(self):
        number_custom_link_before = CustomLink.objects.all().count()
        response = self.client.post(self.get_custom_link_create_url, data=self.post_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        check_data_in_dict(self, [self.post_data], [response.data])
        self.assertEqual(number_custom_link_before + 1, CustomLink.objects.all().count())

    def test_admin_cannot_post_custom_link_not_full(self):
        self.post_data.pop('name')
        response = self.client.post(self.get_custom_link_create_url, data=self.post_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_customer_cannot_post_custom_link(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.post(self.get_custom_link_create_url, data=self.post_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_post_operation_when_logout(self):
        self.client.logout()
        response = self.client.post(self.get_custom_link_create_url, data=self.post_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
