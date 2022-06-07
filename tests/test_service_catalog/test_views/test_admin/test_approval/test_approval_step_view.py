from django.urls import reverse

from service_catalog.models import ApprovalWorkflow
from service_catalog.models.approval_step import ApprovalStep
from service_catalog.models.approval_step_type import ApprovalStepType
from tests.test_service_catalog.base_approval import BaseApproval


class TestApprovalStepViews(BaseApproval):

    def setUp(self):
        super(TestApprovalStepViews, self).setUp()
        self.kwargs_list = {
            "approval_workflow_id": self.test_approval_workflow.id,
        }
        self.kwargs_detail = {
            "approval_workflow_id": self.test_approval_workflow.id,
            "approval_step_id": self.test_approval_step_1.id
        }
        self.edit_approval_step_data = {
            "name": "new_approval_step_name",
            "type": ApprovalStepType.AT_LEAST_ONE,
            "teams": [self.test_team.id],
        }

    def test_admin_can_create_an_approval_step(self):
        old_count = ApprovalStep.objects.count()
        new_workflow = ApprovalWorkflow.objects.create(name='new workflow')
        self.assertIsNone(new_workflow.entry_point)
        self.kwargs_list["approval_workflow_id"] = new_workflow.id
        url = reverse('service_catalog:approval_step_create', kwargs=self.kwargs_list)
        response = self.client.post(url, data=self.edit_approval_step_data)
        self.assertEqual(302, response.status_code)
        new_workflow.refresh_from_db()
        self.assertEqual(old_count + 1, ApprovalStep.objects.count())
        self.assertIsNotNone(new_workflow.entry_point)

    def test_admin_cannot_create_an_approval_step_in_approval_workflow_with_entry_point(self):
        old_count = ApprovalStep.objects.count()
        self.assertIsNotNone(self.test_approval_workflow.entry_point)
        url = reverse('service_catalog:approval_step_create', kwargs=self.kwargs_list)
        response = self.client.post(url, data=self.edit_approval_step_data)
        self.assertEqual(403, response.status_code)
        self.assertEqual(old_count, ApprovalStep.objects.count())

    def test_admin_can_create_next_approval_step(self):
        old_count = ApprovalStep.objects.count()
        url = reverse('service_catalog:approval_step_create', kwargs=self.kwargs_list) + "?previous_id=" + str(self.test_approval_step_3.id)
        response = self.client.post(url, data=self.edit_approval_step_data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(old_count + 1, ApprovalStep.objects.count())
        self.test_approval_step_3.refresh_from_db()
        self.test_approval_step_3.next.name = self.edit_approval_step_data.get('name')
        self.assertIsNone(self.test_approval_step_3.next.next)

    def test_admin_can_create_next_approval_step_between_two_step(self):
        old_count = ApprovalStep.objects.count()
        url = reverse('service_catalog:approval_step_create', kwargs=self.kwargs_list) + "?previous_id=" + str(self.test_approval_step_1.id)
        response = self.client.post(url, data=self.edit_approval_step_data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(old_count + 1, ApprovalStep.objects.count())
        self.test_approval_step_1.refresh_from_db()
        self.test_approval_step_1.next.name = self.edit_approval_step_data.get('name')
        self.assertEqual(self.test_approval_step_1.next.next, self.test_approval_step_2)

    def test_admin_cannot_create_next_approval_step_in_other_workflow(self):
        old_count = ApprovalStep.objects.count()
        new_workflow = ApprovalWorkflow.objects.create(name="test new approval workflow")
        url = reverse('service_catalog:approval_step_create',
                      kwargs={"approval_workflow_id": new_workflow.id}) + "?previous_id=" + str(self.test_approval_step_3.id)
        response = self.client.post(url, data=self.edit_approval_step_data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(old_count, ApprovalStep.objects.count())

    def test_customer_cannot_create_next_approval_step(self):
        self.client.force_login(user=self.standard_user)
        old_count = ApprovalStep.objects.count()
        url = reverse('service_catalog:approval_step_create', kwargs=self.kwargs_list) + "?previous_id=" + str(self.test_approval_step_3.id)
        response = self.client.post(url, data=self.edit_approval_step_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(old_count, ApprovalStep.objects.count())

    def test_cannot_create_approval_step_when_logout(self):
        self.client.logout()
        old_count = ApprovalStep.objects.count()
        url = reverse('service_catalog:approval_step_create', kwargs=self.kwargs_list) + "?previous_id=" + str(self.test_approval_step_3.id)
        response = self.client.post(url, data=self.edit_approval_step_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(old_count, ApprovalStep.objects.count())

    def test_edit_approval_step(self):
        url = reverse('service_catalog:approval_step_edit', kwargs=self.kwargs_detail)
        response = self.client.post(url, data=self.edit_approval_step_data)
        self.assertEqual(302, response.status_code)
        self.test_approval_step_1.refresh_from_db()
        self.assertEqual(self.test_approval_step_1.name, "new_approval_step_name")

    def test_customer_cannot_edit_approval_step(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        url = reverse('service_catalog:approval_step_edit', kwargs=self.kwargs_detail)
        response = self.client.post(url, data=self.edit_approval_step_data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(self.test_approval_step_1.name, "First")

    def test_admin_can_delete_the_workflow_entry_point(self):
        url = reverse('service_catalog:approval_step_delete', kwargs=self.kwargs_detail)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.client.post(url)
        self.assertFalse(ApprovalStep.objects.filter(id=self.test_approval_step_1.id).exists())
        self.test_approval_workflow.refresh_from_db()
        self.assertEqual(self.test_approval_workflow.entry_point, self.test_approval_step_2)

    def test_admin_can_delete_approval_step_between_two_approval_step(self):
        self.kwargs_detail['approval_step_id'] = self.test_approval_step_2.id
        url = reverse('service_catalog:approval_step_delete', kwargs=self.kwargs_detail)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.client.post(url)
        self.assertFalse(ApprovalStep.objects.filter(id=self.test_approval_step_2.id).exists())
        self.test_approval_step_1.refresh_from_db()
        self.assertEqual(self.test_approval_step_1.next, self.test_approval_step_3)

    def test_customer_cannot_delete_approval_step(self):
        self.client.force_login(self.standard_user)
        url = reverse('service_catalog:approval_step_delete', kwargs=self.kwargs_detail)
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        self.client.post(url)
        self.assertTrue(ApprovalStep.objects.filter(id=self.test_approval_step_1.id).exists())
