from django.urls import reverse

from tests.test_service_catalog.base import BaseTest


class RequestHooksListViewsTest(BaseTest):

    def setUp(self):
        super(RequestHooksListViewsTest, self).setUp()
        self.url = reverse('service_catalog:requesthook_list')

    def test_get_list(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_user_cannot_list(self):
        self.client.logout()
        self.client.login(username=self.standard_user, password=self.common_password)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)
