import json
import copy
from unittest import mock
from unittest.mock import MagicMock

from django.urls import reverse

from service_catalog.models import JobTemplate
from tests.test_service_catalog.test_views.test_admin.test_tools.test_tower.base_test_tower import BaseTestTower


class AdminTowerGetViewsTest(BaseTestTower):

    def setUp(self):
        super(AdminTowerGetViewsTest, self).setUp()
        self.args = {
            'tower_id': self.tower_server_test.id,
        }

    def test_towerserver_sync(self):
        with mock.patch("service_catalog.models.tower_server.TowerServer.sync") as mock_sync:
            url = reverse('service_catalog:towerserver_sync', kwargs=self.args)
            response = self.client.post(url)
            self.assertEqual(202, response.status_code)
            data = json.loads(response.content)
            mock_sync.assert_called()
            self.assertTrue("task_id" in data)

    def test_towerserver_sync_when_added_job_template(self):
        self.mock_tower_sync(4)

    def test_towerserver_sync_when_deleted_job_template(self):
        self.mock_tower_sync(-1)

    def mock_tower_sync(self, delta):
        with mock.patch('service_catalog.models.tower_server.TowerServer.get_tower_instance') as mock_tower_instance:
            current_number_job_template = JobTemplate.objects.filter(tower_server=self.tower_server_test).count()
            target_number_job_template = current_number_job_template + delta
            job_template_list = list()
            for i in range(target_number_job_template):
                magic_mock = MagicMock(
                    id=i + 100,
                    survey_spec=self.testing_survey,
                    _data=self.job_template_testing_data
                )
                magic_mock.name = f"Test {i}"
                job_template_list.append(magic_mock)
            mock_tower_instance.return_value = MagicMock(
                job_templates=job_template_list
            )
            self.tower_server_test.sync()
            self.tower_server_test.refresh_from_db()
            mock_tower_instance.assert_called()
            # assert that the survey is the same
            self.assertEqual(JobTemplate.objects.filter(tower_server=self.tower_server_test).count(),
                             target_number_job_template)

    def test_sync_job_template(self):
        with mock.patch("service_catalog.models.tower_server.TowerServer.sync") as mock_sync:
            args = copy.copy(self.args)
            args['pk'] = self.job_template_test.id
            url = reverse('service_catalog:sync_job_template', kwargs=args)
            response = self.client.post(url)
            self.assertEqual(202, response.status_code)
            data = json.loads(response.content)
            mock_sync.assert_called()
            self.assertTrue("task_id" in data)

    def test_user_cannot_towerserver_sync(self):
        with mock.patch("service_catalog.models.tower_server.TowerServer.sync") as mock_sync:
            self.client.login(username=self.standard_user, password=self.common_password)
            url = reverse('service_catalog:towerserver_sync', kwargs=self.args)
            response = self.client.post(url)
            self.assertEqual(403, response.status_code)
            mock_sync.assert_not_called()

    def test_user_cannot_sync_job_template(self):
        with mock.patch("service_catalog.models.tower_server.TowerServer.sync") as mock_sync:
            self.client.login(username=self.standard_user, password=self.common_password)
            args = copy.copy(self.args)
            args['pk'] = self.job_template_test.id
            url = reverse('service_catalog:sync_job_template', kwargs=args)
            response = self.client.post(url)
            self.assertEqual(403, response.status_code)
            mock_sync.assert_not_called()

    def test_jobtemplate_list(self):
        url = reverse('service_catalog:jobtemplate_list', kwargs=self.args)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(JobTemplate.objects.filter(tower_server=self.tower_server_test).count(),
                         len(response.context["table"].data.data))

    def test_cannot_get_jobtemplate_list_when_logout(self):
        self.client.logout()
        url = reverse('service_catalog:jobtemplate_list', kwargs=self.args)
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)

    def test_tower_job_templates_compliancy_list(self):
        args = copy.copy(self.args)
        args['pk'] = self.job_template_test.id
        url = reverse('service_catalog:job_template_compliancy', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_cannot_get_tower_job_templates_compliancy_list_when_logout(self):
        self.client.logout()
        args = copy.copy(self.args)
        args['pk'] = self.job_template_test.id
        url = reverse('service_catalog:job_template_compliancy', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)

    def test_get_tower_job_templates_details(self):
        args = copy.copy(self.args)
        args['pk'] = self.job_template_test.id
        url = reverse('service_catalog:jobtemplate_details', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_customer_cannot_get_tower_job_templates_details(self):
        self.client.logout()
        self.client.login(username=self.standard_user, password=self.common_password)
        self._cannot_get_job_templates_details(expected_status=403)

    def test_cannot_get_tower_job_templates_details_when_logout(self):
        self.client.logout()
        self._cannot_get_job_templates_details(expected_status=302)

    def _cannot_get_job_templates_details(self, expected_status):
        args = copy.copy(self.args)
        args['pk'] = self.job_template_test.id
        url = reverse('service_catalog:jobtemplate_details', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(expected_status, response.status_code)
