from django.urls import reverse

from service_catalog.models.approval_workflow import ApprovalWorkflow
from tests.test_service_catalog.base_approval import BaseApproval


class TestApprovalWorkflowViews(BaseApproval):

    def setUp(self):
        super(TestApprovalWorkflowViews, self).setUp()
        self.kwargs_detail = {
            "approval_workflow_id": self.test_approval_workflow.id
        }
        self.edit_approval_workflow_data = {
            "name": "new_approval_workflow_name"
        }

    def test_admin_can_create_an_approval_workflow(self):
        old_count = ApprovalWorkflow.objects.count()
        url = reverse('service_catalog:approval_workflow_create')
        response = self.client.post(url, data=self.edit_approval_workflow_data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(old_count + 1, ApprovalWorkflow.objects.count())
        self.assertEqual(ApprovalWorkflow.objects.latest('id').name, self.edit_approval_workflow_data.get('name'))

    def test_customer_cannot_create_approval_workflow(self):
        self.client.force_login(user=self.standard_user)
        old_count = ApprovalWorkflow.objects.count()
        url = reverse('service_catalog:approval_workflow_create')
        response = self.client.post(url, data=self.edit_approval_workflow_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(old_count, ApprovalWorkflow.objects.count())

    def test_cannot_create_approval_workflow_when_logout(self):
        self.client.logout()
        old_count = ApprovalWorkflow.objects.count()
        url = reverse('service_catalog:approval_workflow_create')
        response = self.client.post(url, data=self.edit_approval_workflow_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(old_count, ApprovalWorkflow.objects.count())

    def test_admin_can_get_approval_workflow_list(self):
        url = reverse('service_catalog:approval_workflow_list')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["table"].data.data), 1)

    def test_customer_cannot_get_approval_workflow_list(self):
        self.client.force_login(self.standard_user)
        url = reverse('service_catalog:approval_workflow_list')
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

    def test_cannot_get_approval_workflow_list_when_logout(self):
        self.client.logout()
        url = reverse('service_catalog:approval_workflow_list')
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)

    def test_edit_approval_workflow(self):
        url = reverse('service_catalog:approval_workflow_edit', kwargs=self.kwargs_detail)
        response = self.client.post(url, data=self.edit_approval_workflow_data)
        self.assertEqual(302, response.status_code)
        self.test_approval_workflow.refresh_from_db()
        self.assertEqual(self.test_approval_workflow.name, self.edit_approval_workflow_data.get('name'))

    def test_customer_cannot_edit_approval_workflow(self):
        old_name = self.test_approval_workflow.name
        self.client.login(username=self.standard_user, password=self.common_password)
        url = reverse('service_catalog:approval_workflow_edit', kwargs=self.kwargs_detail)
        response = self.client.post(url, data=self.edit_approval_workflow_data)
        self.test_approval_workflow.refresh_from_db()
        self.assertEqual(302, response.status_code)
        self.assertEqual(self.test_approval_workflow.name, old_name)

    def test_admin_can_delete_the_workflow_entry_point(self):
        url = reverse('service_catalog:approval_workflow_delete', kwargs=self.kwargs_detail)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.client.post(url)
        self.assertFalse(ApprovalWorkflow.objects.filter(id=self.test_approval_workflow.id).exists())

    def test_customer_cannot_delete_approval_workflow(self):
        self.client.force_login(self.standard_user)
        url = reverse('service_catalog:approval_workflow_delete', kwargs=self.kwargs_detail)
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        self.client.post(url)
        self.assertTrue(ApprovalWorkflow.objects.filter(id=self.test_approval_workflow.id).exists())
