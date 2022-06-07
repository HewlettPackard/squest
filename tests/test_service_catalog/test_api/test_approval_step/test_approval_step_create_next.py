from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import ApprovalWorkflow, ApprovalStep
from service_catalog.models.approval_step_type import ApprovalStepType
from tests.test_service_catalog.base_approval import BaseApproval
from tests.utils import check_data_in_dict


class TestApiApprovalStepListCreateNext(BaseApproval):

    def setUp(self):
        super(TestApiApprovalStepListCreateNext, self).setUp()
        self.post_data = {
            "name": "new_approval_step_name",
            "type": ApprovalStepType.AT_LEAST_ONE,
            "teams": [self.test_team.id],
            "next": None,
            "previous_id": self.test_approval_step_3.id
        }
        self.create_approval_step_url = reverse('api_approval_step_list_create',
                                                kwargs={'approval_workflow_id': self.test_approval_workflow.id})

    def _create_next_approval_step(self):
        response = self.client.post(self.create_approval_step_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.post_data.pop('previous_id')
        self.post_data.pop('next')
        check_data_in_dict(self, [self.post_data], [response.data])
        self.assertIn("id", response.data)
        self.assertIn("name", response.data)
        self.assertIn("type", response.data)
        self.assertIn("teams", response.data)
        self.assertIn("next", response.data)
        self.assertIn("position", response.data)
        return response

    def _create_approval_step_failed(self, status_error=status.HTTP_400_BAD_REQUEST):
        response = self.client.post(self.create_approval_step_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status_error)
        return response

    def test_admin_can_create_next_approval_step(self):
        self._create_next_approval_step()

    def test_admin_can_insert_approval_step_between_two_step(self):
        self.post_data['previous_id'] = self.test_approval_step_1.id
        self.create_approval_step_url = reverse('api_approval_step_list_create',
                                                kwargs={'approval_workflow_id': self.test_approval_workflow.id})
        response = self._create_next_approval_step()
        new_approval = ApprovalStep.objects.get(id=response.data['id'])
        self.test_approval_step_1.refresh_from_db()
        self.assertEqual(self.test_approval_step_1.next, new_approval)
        self.assertEqual(new_approval.next, self.test_approval_step_2)

    def test_admin_cannot_create_next_approval_step_in_other_workflow(self):
        self.post_data['previous_id'] = self.test_approval_step_3.id
        new_workflow = ApprovalWorkflow.objects.create(name="test new approval workflow")
        self.create_approval_step_url = reverse('api_approval_step_list_create',
                                                kwargs={'approval_workflow_id': new_workflow.id})
        self._create_approval_step_failed(status_error=status.HTTP_404_NOT_FOUND)

    def test_customer_cannot_create_next_approval_step(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.post(self.create_approval_step_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_create_approval_step_when_logout(self):
        self.client.logout()
        response = self.client.post(self.create_approval_step_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
