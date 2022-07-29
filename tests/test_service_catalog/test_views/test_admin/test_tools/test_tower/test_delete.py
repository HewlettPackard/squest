from django.urls import reverse

from service_catalog.models import TowerServer, JobTemplate, Service, OperationType
from tests.test_service_catalog.test_views.test_admin.test_tools.test_tower.base_test_tower import BaseTestTower


class AdminTowerDeleteViewsTest(BaseTestTower):

    def setUp(self):
        super(AdminTowerDeleteViewsTest, self).setUp()
        self.args = {
            'tower_id': self.tower_server_test.id,
        }
        self.url = reverse('service_catalog:delete_tower', kwargs=self.args)

    def test_get_page(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_admin_can_delete_tower_server(self):
        id_to_delete = self.tower_server_test.id
        response = self.client.post(self.url)
        self.assertEqual(302, response.status_code)
        self.assertFalse(TowerServer.objects.filter(id=id_to_delete).exists())

    def test_user_cannot_delete_tower_server(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        id_to_delete = self.tower_server_test.id
        response = self.client.post(self.url)
        self.assertEqual(302, response.status_code)
        self.assertTrue(TowerServer.objects.filter(id=id_to_delete).exists())

    def test_admin_can_delete_job_template(self):
        services = [service for service in Service.objects.filter(operation__job_template=self.job_template_test,
                                                                  operation__type__exact=OperationType.CREATE)]
        args = {
            'tower_id': self.tower_server_test.id,
            'job_template_id': self.job_template_test.id
        }
        url = reverse('service_catalog:delete_job_template', kwargs=args)
        id_to_delete = self.job_template_test.id
        response = self.client.post(url)
        self.assertEqual(302, response.status_code)
        self.assertFalse(JobTemplate.objects.filter(id=id_to_delete).exists())
        for service in services:
            service.refresh_from_db()
            self.assertIsNotNone(service.operations.filter(type=OperationType.CREATE).first())
            self.assertIsNone(service.operations.filter(type=OperationType.CREATE).first().job_template)
            self.assertFalse(service.enabled)

    def test_user_cannot_delete_job_template(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        args = {
            'tower_id': self.tower_server_test.id,
            'job_template_id': self.job_template_test.id
        }
        url = reverse('service_catalog:delete_job_template', kwargs=args)
        id_to_delete = self.job_template_test.id
        response = self.client.post(url)
        self.assertEqual(302, response.status_code)
        self.assertTrue(JobTemplate.objects.filter(id=id_to_delete).exists())

    def test_can_reach_delete_job_template_page(self):
        args = {
            'tower_id': self.tower_server_test.id,
        }
        url = reverse('service_catalog:delete_tower', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_cannot_delete_job_template_page_when_logout(self):
        self.client.logout()
        args = {
            'tower_id': self.tower_server_test.id,
        }
        url = reverse('service_catalog:delete_tower', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
