from django.urls import reverse

from tests.test_views.admin.settings.tower.base_test_tower import BaseTestTower


class AdminTowerListViewsTest(BaseTestTower):

    def setUp(self):
        super(AdminTowerListViewsTest, self).setUp()
        self.url = reverse('service_catalog:list_tower')

    def test_admin_can_list_tower_server(self):
        response = self.client.get(self.url)
        self.assertEquals(200, response.status_code)
        self.assertTrue("tower_servers" in response.context)
        self.assertEquals(1, len(response.context["tower_servers"]))

    def test_user_cannot_list_tower_server(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        response = self.client.get(self.url)
        self.assertEquals(302, response.status_code)
