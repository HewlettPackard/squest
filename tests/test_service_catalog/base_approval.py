from profiles.models import Team
from service_catalog.models import ApprovalWorkflow, Instance, Request
from service_catalog.models.approval_step import ApprovalStep
from service_catalog.models.approval_step_type import ApprovalStepType
from tests.test_profile.test_group.test_group_base import TestGroupBase


class BaseApproval(TestGroupBase):

    def setUp(self):
        super(BaseApproval, self).setUp()
        self.test_approval_workflow = ApprovalWorkflow.objects.create(name="test approval workflow")
        self.test_approval_step_3 = ApprovalStep.objects.create(
            name="Third",
            type=ApprovalStepType.ALL_OF_THEM,
            approval_workflow=self.test_approval_workflow
        )
        self.test_approval_step_3.teams.set(Team.objects.filter(id__in=[self.test_team.id]))
        self.test_approval_step_2 = ApprovalStep.objects.create(
            name="Second",
            type=ApprovalStepType.ALL_OF_THEM,
            next=self.test_approval_step_3,
            approval_workflow=self.test_approval_workflow
        )
        self.test_approval_step_2.teams.set(Team.objects.filter(id__in=[self.test_team.id, self.test_team2.id]))
        self.test_approval_step_1 = ApprovalStep.objects.create(
            name="First",
            type=ApprovalStepType.AT_LEAST_ONE,
            next=self.test_approval_step_2,
            approval_workflow=self.test_approval_workflow
        )
        self.test_approval_workflow.entry_point = self.test_approval_step_1
        self.test_approval_workflow.save()
        self.test_approval_step_1.teams.set(Team.objects.filter(id__in=[self.test_team.id, self.test_team2.id]))
        for user in [self.my_user, self.my_user2, self.my_user3, self.my_user4]:
            user.is_staff = True
            user.is_superuser = True
            user.save()
        self.create_operation_test.approval_workflow = self.test_approval_workflow
        self.create_operation_test.save()
        self.test_instance = Instance.objects.create(name="test_instance_1", service=self.service_test,
                                                     requester=self.standard_user)
        form_data = {'text_variable': 'my_var'}
        self.test_request = Request.objects.create(fill_in_survey=form_data,
                                                   instance=self.test_instance,
                                                   operation=self.create_operation_test,
                                                   user=self.standard_user)
        self.test_request.admin_fill_in_survey = {
            'multiplechoice_variable': "choice1",
            'multiselect_var': ["multiselect_3", "multiselect_2"],
            'textarea_var': "textarea_val",
            'password_var': "password_val",
            'float_var': 1.5,
            'integer_var': 1
        }
        self.test_request.save()
