import json

from profiles.models import Permission
from service_catalog.models import ApprovalWorkflow, ApprovalStep
from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint, \
    TestingPutContextView


class TestServiceCatalogPermissionsViews(BaseTestRequest, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.approval_workflow = ApprovalWorkflow.objects.create(
            name="test_approval_workflow",
            operation=self.create_operation_test
        )
        self.approval_step = ApprovalStep.objects.create(
            name="test_approval_step_1",
            approval_workflow=self.approval_workflow
        )
        self.approval_step_2 = ApprovalStep.objects.create(
            name="test_approval_step_2",
            approval_workflow=self.approval_workflow
        )

    def test_approvalstep_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='service_catalog:approvalstep_create',
                perm_str='service_catalog.add_approvalstep',
                url_kwargs={'approval_workflow_id': self.approval_workflow.id},
            ),
            TestingPostContextView(
                url='service_catalog:approvalstep_create',
                perm_str='service_catalog.add_approvalstep',
                url_kwargs={'approval_workflow_id': self.approval_workflow.id},
                data={
                    'name': 'New approval step',
                    'permission': Permission.objects.get(codename='approve_reject_approvalstep').id,
                    'readable_fields': [],
                    'editable_fields': [],
                    'approval_workflow': self.approval_workflow.id
                }
            ),
            TestingGetContextView(
                url='service_catalog:approvalstep_edit',
                perm_str='service_catalog.change_approvalstep',
                url_kwargs={'approval_workflow_id': self.approval_workflow.id, 'pk': self.approval_step.id}
            ),
            TestingPutContextView(
                url='service_catalog:approvalstep_edit',
                perm_str='service_catalog.change_approvalstep',
                url_kwargs={'approval_workflow_id': self.approval_workflow.id, 'pk': self.approval_step.id},
                data={
                    'name': 'Approval step update',
                    'permission': Permission.objects.get(codename='approve_reject_approvalstep').id,
                    'readable_fields': [],
                    'editable_fields': [],
                    'approval_workflow': self.approval_workflow.id
                }
            ),
            TestingGetContextView(
                url='service_catalog:ajax_approval_step_position_update',
                perm_str='service_catalog.change_approvalstep',
                expected_status_code=405,
                expected_not_allowed_status_code=405,
            ),
            TestingPostContextView(
                url='service_catalog:ajax_approval_step_position_update',
                perm_str='service_catalog.change_approvalstep',
                data={
                    'listStepToUpdate': json.dumps([
                        {
                            "position": self.approval_step_2.position,
                            "id": self.approval_step.id
                        }, {
                            "position": self.approval_step.position,
                            "id": self.approval_step_2.id
                        }
                    ])
                },
                expected_status_code=202
            ),

            TestingGetContextView(
                url='service_catalog:approvalstep_delete',
                perm_str='service_catalog.delete_approvalstep',
                url_kwargs={'approval_workflow_id': self.approval_workflow.id, 'pk': self.approval_step.id}
            ),
            TestingPostContextView(
                url='service_catalog:approvalstep_delete',
                perm_str='service_catalog.delete_approvalstep',
                url_kwargs={'approval_workflow_id': self.approval_workflow.id, 'pk': self.approval_step.id}
            ),
        ]
        self.run_permissions_tests(testing_view_list)
