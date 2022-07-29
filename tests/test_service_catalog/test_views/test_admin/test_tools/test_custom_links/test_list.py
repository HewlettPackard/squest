from django.urls import reverse

from tests.test_service_catalog.test_views.test_admin.test_tools.test_custom_links.base_test_custom_link import \
    BaseTestCustomLink


class CustomLinksListViewsTest(BaseTestCustomLink):

    def setUp(self):
        super(CustomLinksListViewsTest, self).setUp()
        self.url = reverse('service_catalog:custom_link_list')

    def test_get_list(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["table"].data.data), 1)

    def test_user_cannot_list(self):
        self.client.logout()
        self.client.login(username=self.standard_user, password=self.common_password)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)
