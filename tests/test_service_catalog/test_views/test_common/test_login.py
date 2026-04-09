from django.urls import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestLogin(BaseTestRequest):
    def setUp(self):
        super(TestLogin, self).setUp()
        self.url = reverse('login')

    def test_get_login(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
