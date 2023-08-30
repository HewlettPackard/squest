from profiles.models import Permission
from service_catalog.models import ApprovalWorkflow, ApprovalStep
from tests.permission_endpoint import TestPermissionEndpoint, TestingGetContextView, TestingPostContextView, \
    TestingPatchContextView, TestingPutContextView, TestingDeleteContextView
from tests.test_service_catalog.base_test_request import BaseTestRequestAPI


class TestServiceCatalogApprovalStepPermissionsEndpoint(BaseTestRequestAPI, TestPermissionEndpoint):
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
                url='api_approvalstep_list_create',
                perm_str='service_catalog.list_approvalstep',
            ),
            TestingPostContextView(
                url='api_approvalstep_list_create',
                perm_str='service_catalog.add_approvalstep',
                data={
                    'approval_workflow': self.approval_workflow.id,
                    'name': 'New approval step',
                    'permission': Permission.objects.filter(content_type__model='approvalstep').first().id,
                    'readable_fields': [],
                    'editable_fields': [],
                }
            ),
            TestingGetContextView(
                url='api_approvalstep_details',
                perm_str='service_catalog.view_approvalstep',
                url_kwargs={'pk': self.approval_step.id}
            ),
            TestingPutContextView(
                url='api_approvalstep_details',
                perm_str='service_catalog.change_approvalstep',
                data={
                    'approval_workflow': self.approval_workflow.id,
                    'name': 'Approval step PUT',
                    'permission': Permission.objects.filter(content_type__model='approvalstep').first().id,
                    'readable_fields': [],
                    'editable_fields': [],
                },
                url_kwargs={'pk': self.approval_step.id}
            ),
            TestingPatchContextView(
                url='api_approvalstep_details',
                perm_str='service_catalog.change_approvalstep',
                data={
                    'name': 'Approval step PATCH'
                },
                url_kwargs={'pk': self.approval_step.id}
            ),
            TestingDeleteContextView(
                url='api_approvalstep_details',
                perm_str='service_catalog.delete_approvalstep',
                url_kwargs={'pk': self.approval_step.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)
