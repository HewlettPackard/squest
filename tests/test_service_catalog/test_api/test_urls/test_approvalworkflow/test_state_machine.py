from profiles.models import Permission
from service_catalog.models import ApprovalWorkflow, ApprovalStep, Instance, Request
from tests.permission_endpoint import TestPermissionEndpoint, TestingGetContextView, TestingPostContextView
from tests.test_service_catalog.base import BaseTestAPI


class TestServiceCatalogApprovalWorkflowPermissionsEndpoint(BaseTestAPI, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        # Create approval workflow
        self.approval_worklflow = ApprovalWorkflow.objects.create(operation=self.create_operation_test,
                                                                  enabled=True)
        self.approval_worklflow.scopes.set([self.test_quota_scope])
        self.approval_worklflow.save()

        self.approval_step1 = ApprovalStep(name="Step 1", approval_workflow=self.approval_worklflow)
        self.approval_step1.permission = Permission.objects.get_by_natural_key(codename="approve_reject_approvalstep",
                                                                               app_label="service_catalog",
                                                                               model="approvalstep")
        self.approval_step1.save()

        self.test_instance = Instance.objects.create(name="test_instance_1",
                                                     service=self.service_test,
                                                     spec={
                                                         "value1": "key1"
                                                     },
                                                     requester=self.standard_user,
                                                     quota_scope=self.test_quota_scope)
        self.test_request = Request.objects.create(
            fill_in_survey={
                'text_variable': 'my_var',
                'multiplechoice_variable': 'choice1', 'multiselect_var': 'multiselect_1',
                'textarea_var': '2',
                'password_var': 'pass',
                'integer_var': '1',
                'float_var': '0.6'
            },
            instance=self.test_instance,
            operation=self.create_operation_test,
            user=self.standard_user)

    def test_approvalworkflow_approve(self):
        testing_view_list = [
            TestingGetContextView(
                url='api_request_approval_workflow_state_approve',
                url_kwargs={'pk': self.test_request.pk},
                perm_str='service_catalog.approve_reject_approvalstep',
            ),
            TestingPostContextView(
                url='api_request_approval_workflow_state_approve',
                url_kwargs={'pk': self.test_request.pk},
                perm_str='service_catalog.approve_reject_approvalstep',
                expected_status_code=200
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_approvalworkflow_reject(self):
        testing_view_list = [
            TestingGetContextView(
                url='api_request_approval_workflow_state_reject',
                url_kwargs={'pk': self.test_request.pk},
                perm_str='service_catalog.approve_reject_approvalstep',
            ),
            TestingPostContextView(
                url='api_request_approval_workflow_state_reject',
                url_kwargs={'pk': self.test_request.pk},
                perm_str='service_catalog.approve_reject_approvalstep',
                expected_status_code=200
            )
        ]
        self.run_permissions_tests(testing_view_list)
