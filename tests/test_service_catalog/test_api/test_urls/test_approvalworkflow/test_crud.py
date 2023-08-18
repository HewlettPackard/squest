from service_catalog.models import ApprovalWorkflow
from tests.permission_endpoint import TestPermissionEndpoint, TestingGetContextView, TestingPostContextView, \
    TestingPatchContextView, TestingPutContextView, TestingDeleteContextView
from tests.test_service_catalog.base_test_request import BaseTestRequestAPI


class TestServiceCatalogApprovalWorkflowPermissionsEndpoint(BaseTestRequestAPI, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.approval_workflow = ApprovalWorkflow.objects.create(
            name="test_approval_workflow",
            operation=self.create_operation_test
        )

    def test_approvalworkflow_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='api_approvalworkflow_list_create',
                perm_str='service_catalog.list_approvalworkflow',
            ),
            TestingPostContextView(
                url='api_approvalworkflow_list_create',
                perm_str='service_catalog.add_approvalworkflow',
                data={
                    'name': 'New approval workflow',
                    'operation': self.update_operation_test.id,
                    'scope': self.test_quota_scope.id,
                }
            ),
            TestingGetContextView(
                url='api_approvalworkflow_details',
                perm_str='service_catalog.view_approvalworkflow',
                url_kwargs={'pk': self.approval_workflow.id}
            ),
            TestingPutContextView(
                url='api_approvalworkflow_details',
                perm_str='service_catalog.change_approvalworkflow',
                data={
                    'name': 'Approval workflow PUT',
                    'operation': self.create_operation_test.id,
                    'scope': self.test_quota_scope.id,
                },
                url_kwargs={'pk': self.approval_workflow.id}
            ),
            TestingPatchContextView(
                url='api_approvalworkflow_details',
                perm_str='service_catalog.change_approvalworkflow',
                data={
                    'name': 'Approval workflow PATCH',
                },
                url_kwargs={'pk': self.approval_workflow.id}
            ),
            TestingDeleteContextView(
                url='api_approvalworkflow_details',
                perm_str='service_catalog.delete_approvalworkflow',
                url_kwargs={'pk': self.approval_workflow.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)
