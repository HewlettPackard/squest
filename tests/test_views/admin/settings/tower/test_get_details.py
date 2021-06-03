import json
from unittest import mock

from django.urls import reverse

from tests.test_views.admin.settings.tower.base_test_tower import BaseTestTower


class AdminTowerGetViewsTest(BaseTestTower):

    def setUp(self):
        super(AdminTowerGetViewsTest, self).setUp()
        self.args = {
            'tower_id': self.tower_server_test.id,
        }

    def test_sync_tower(self):
        with mock.patch("service_catalog.models.tower_server.TowerServer.sync") as mock_sync:
            url = reverse('sync_tower', kwargs=self.args)
            response = self.client.post(url)
            self.assertEquals(202, response.status_code)
            data = json.loads(response.content)
            mock_sync.assert_called()
            self.assertTrue("task_id" in data)

    def test_user_cannot_sync_tower(self):
        with mock.patch("service_catalog.models.tower_server.TowerServer.sync") as mock_sync:
            self.client.login(username=self.standard_user, password=self.common_password)
            url = reverse('sync_tower', kwargs=self.args)
            response = self.client.post(url)
            self.assertEquals(302, response.status_code)
            mock_sync.assert_not_called()

    def test_get_task_result(self):
        args = {
            'task_id': self.test_task_result.id
        }
        url = reverse('get_task_result', kwargs=args)
        response = self.client.post(url)
        self.assertEquals(202, response.status_code)
        data = json.loads(response.content)
        self.assertTrue("status" in data)
        self.assertTrue("id" in data)
        self.assertTrue("meta" in data)

    def test_tower_job_templates_list(self):
        url = reverse('tower_job_templates_list', kwargs=self.args)
        response = self.client.get(url)
        self.assertEquals(200, response.status_code)
        self.assertEquals(1, len(response.context["job_templates"]))
