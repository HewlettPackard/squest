from service_catalog.models import ApprovalWorkflow
from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestServiceCatalogApprovalWorkflowPermissionsViews(BaseTestRequest, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.approval_workflow = ApprovalWorkflow.objects.create(
            name="test_approval_workflow",
            operation=self.create_operation_test,
            enabled=True
        )

    def test_approvalworkflow_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='service_catalog:approvalworkflow_list',
                perm_str_list=['service_catalog.list_approvalworkflow'],
            ),
            TestingGetContextView(
                url='service_catalog:approvalworkflow_details',
                perm_str_list=['service_catalog.view_approvalworkflow'],
                url_kwargs={'pk': self.approval_workflow.id}
            ),
            TestingGetContextView(
                url='service_catalog:approvalworkflow_create',
                perm_str_list=['service_catalog.add_approvalworkflow'],
            ),
            TestingPostContextView(
                url='service_catalog:approvalworkflow_create',
                perm_str_list=['service_catalog.add_approvalworkflow'],
                data={
                    'name': 'New approvalworkflow',
                    'operation': self.update_operation_test.id,
                    'scope': self.test_quota_scope.id,
                }
            ),
            TestingGetContextView(
                url='service_catalog:approvalworkflow_edit',
                perm_str_list=['service_catalog.change_approvalworkflow'],
                url_kwargs={'pk': self.approval_workflow.id}
            ),
            TestingGetContextView(
                url='service_catalog:approvalworkflow_preview',
                perm_str_list=['service_catalog.view_approvalworkflow'],
                url_kwargs={'pk': self.approval_workflow.id, 'scope_id': self.test_quota_scope.id}
            ),
            TestingPostContextView(
                url='service_catalog:approvalworkflow_edit',
                perm_str_list=['service_catalog.change_approvalworkflow'],
                url_kwargs={'pk': self.approval_workflow.id},
                data={
                    'name': 'Approvalworkflow updated',
                    'operation': self.create_operation_test.id,
                    'scopes': [self.test_quota_scope.id],
                }
            ),
            TestingGetContextView(
                url='service_catalog:approvalworkflow_reset_requests',
                perm_str_list=['service_catalog.re_submit_request'],
                url_kwargs={'pk': self.approval_workflow.id}
            ),
            TestingPostContextView(
                url='service_catalog:approvalworkflow_reset_requests',
                perm_str_list=['service_catalog.re_submit_request'],
                url_kwargs={'pk': self.approval_workflow.id}
            ),
            TestingGetContextView(
                url='service_catalog:approvalworkflow_delete',
                perm_str_list=['service_catalog.delete_approvalworkflow'],
                url_kwargs={'pk': self.approval_workflow.id}
            ),
            TestingPostContextView(
                url='service_catalog:approvalworkflow_delete',
                perm_str_list=['service_catalog.delete_approvalworkflow'],
                url_kwargs={'pk': self.approval_workflow.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)