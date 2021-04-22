from django.urls import reverse

from service_catalog.models import TowerServer, JobTemplate
from tests.test_views.admin.tower.base_test_tower import BaseTestTower


class AdminTowerDeleteViewsTest(BaseTestTower):

    def setUp(self):
        super(AdminTowerDeleteViewsTest, self).setUp()
        self.args = {
            'tower_id': self.tower_server_test.id,
        }
        self.url = reverse('delete_tower', kwargs=self.args)

    def test_admin_can_delete_tower_server(self):
        id_to_delete = self.tower_server_test.id
        response = self.client.post(self.url)
        self.assertEquals(302, response.status_code)
        self.assertFalse(TowerServer.objects.filter(id=id_to_delete).exists())

    def test_admin_can_delete_job_template(self):
        args = {
            'tower_id': self.tower_server_test.id,
            'job_template_id': self.job_template_test.id
        }
        url = reverse('delete_job_template', kwargs=args)
        id_to_delete = self.job_template_test.id
        response = self.client.post(url)
        self.assertEquals(302, response.status_code)
        self.assertFalse(JobTemplate.objects.filter(id=id_to_delete).exists())
