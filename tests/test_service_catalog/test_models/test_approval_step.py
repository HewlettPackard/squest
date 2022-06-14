from django.core.exceptions import ValidationError

from service_catalog.models import ApprovalStep, ApprovalWorkflow
from service_catalog.models.approval_state import ApprovalState
from service_catalog.models.approval_step_type import ApprovalStepType
from tests.test_service_catalog.base_approval import BaseApproval


class TestApprovalStep(BaseApproval):

    def setUp(self):
        super(TestApprovalStep, self).setUp()

    def test_remove_teams(self):
        self.test_approval_step_2.teams.remove(self.test_team2)
        self.assertEqual({self.test_team}, set(self.test_approval_step_2.teams.all()))
        self.assertEqual(set(self.test_approval_step_2.get_teams_in_role("Approver")),
                         set(self.test_approval_step_2.teams.all()))

    def test_add_teams(self):
        self.test_approval_step_3.teams.add(self.test_team2)
        self.assertEqual({self.test_team, self.test_team2}, set(self.test_approval_step_3.teams.all()))
        self.assertEqual(set(self.test_approval_step_3.get_teams_in_role("Approver")),
                         set(self.test_approval_step_3.teams.all()))

    def test_change_teams(self):
        self.test_approval_step_2.teams.set([self.test_approval_step_2.id])
        self.assertEqual({self.test_team2}, set(self.test_approval_step_2.teams.all()))
        self.assertEqual(set(self.test_approval_step_2.get_teams_in_role("Approver")),
                         set(self.test_approval_step_2.teams.all()))

    def test_cannot_create_a_loop(self):
        self.test_approval_step_3.next = self.test_approval_step_1
        self.assertRaises(ValidationError, self.test_approval_step_3.clean)

    def test_cannot_add_step_with_existing_name_in_the_workflow(self):
        approval_step = ApprovalStep.objects.create(
            name="Name ok",
            type=ApprovalStepType.ALL_OF_THEM,
            approval_workflow=self.test_approval_workflow
        )
        approval_step.add_team_in_role(self.test_team, 'Approver')
        is_raise = False
        try:
            approval_step.clean()
        except ValidationError:
            is_raise = True
        self.assertEqual(is_raise, False)
        approval_step.name = self.test_approval_step_1.name
        self.assertRaises(ValidationError, approval_step.clean)

    def test_can_add_step_with_existing_name_in_another_workflow(self):
        approval_workflow = ApprovalWorkflow.objects.create(name="test2")
        approval_step = ApprovalStep.objects.create(
            name=self.test_approval_step_1.name,
            type=ApprovalStepType.ALL_OF_THEM,
            approval_workflow=approval_workflow
        )
        approval_step.add_team_in_role(self.test_team, 'Approver')
        is_raise = False
        try:
            approval_step.clean()
        except ValidationError:
            is_raise = True
        self.assertEqual(is_raise, False)

    def test_delete_an_approval_step_between_two(self):
        self.test_request.accept(self.test_approval_step_1.teams.first().get_all_users().first())
        self.test_request.refresh_from_db()
        self.assertEqual(self.test_request.approval_step, self.test_approval_step_2)
        self.test_approval_step_2.delete()
        self.test_request.refresh_from_db()
        self.assertEqual(self.test_request.approval_step, self.test_approval_step_3)
        self.test_approval_step_1.refresh_from_db()
        self.assertEqual(self.test_approval_step_1.next, self.test_approval_step_3)

    def test_remove_all_approval_step_in_workflow(self):
        self.test_approval_step_1.delete()
        self.test_request.refresh_from_db()
        self.test_approval_workflow.refresh_from_db()
        self.assertEqual(self.test_request.approval_step, self.test_approval_step_2)
        self.assertEqual(self.test_approval_workflow.entry_point, self.test_approval_step_2)
        self.test_approval_step_2.delete()
        self.test_request.refresh_from_db()
        self.test_approval_workflow.refresh_from_db()
        self.assertEqual(self.test_request.approval_step, self.test_approval_step_3)
        self.assertEqual(self.test_approval_workflow.entry_point, self.test_approval_step_3)
        self.test_approval_step_3.delete()
        self.test_request.refresh_from_db()
        self.test_approval_workflow.refresh_from_db()
        self.assertIsNone(self.test_request.approval_step)
        self.assertIsNone(self.test_approval_workflow.entry_point)

    def test_get_request_approval_state_when_none_state(self):
        result = self.test_request.approval_step.next.get_request_approval_state(self.test_request)
        self.assertEqual(ApprovalState.PENDING, result)
