from service_catalog.models import ApprovalWorkflow, Request, RequestState
from tests.setup import SetupRequest
from tests.utils import TransactionTestUtils

from django.db.models.query import QuerySet


class TestApprovalWorkflowReset(TransactionTestUtils, SetupRequest):

    def setUp(self):
        SetupRequest.setUp(self)

    def _create_approval_for_all(self):
        ##################################
        # Approval workflow for everyone
        ##################################
        aw = ApprovalWorkflow.objects.create(
            name="AW - All scopes",
            operation=self.operation_create_1,
            enabled=True
        )
        return aw

    def _create_approval_for_org2(self):
        ##################################
        # Approval workflow for Org2
        ##################################
        aw = ApprovalWorkflow.objects.create(
            name="AW - Org2",
            operation=self.operation_create_1,
            enabled=True
        )
        aw.scopes.set([self.org2])
        return aw

    def _create_approval_for_org2_team1(self):
        ##################################
        # Approval workflow for Org2 - Team 1
        ##################################
        aw = ApprovalWorkflow.objects.create(
            name="AW - Org2 - Team 1",
            operation=self.operation_create_1,
            enabled=True
        )
        aw.scopes.set([self.team1org2])
        return aw

    def assertRequestUseWorkflow(self, qs, workflow=None):

        if not isinstance(qs, QuerySet):
            qs = Request.objects.filter(id=qs.id)

        for obj in qs:
            if workflow:
                self.assertEqual(obj.approval_workflow_state.approval_workflow, workflow)
            else:
                self.assertIsNotNone(obj.approval_workflow_state)

    def assertRequestDontUseWorkflow(self, qs):
        if not isinstance(qs, QuerySet):
            qs = Request.objects.filter(id=qs.id)
        for obj in qs:
            self.assertIsNone(obj.approval_workflow_state)

    def test_scenario1(self):

        # Scenario: setup a workflow for all

        # Request 1 COMPLETE - Approval NOT USED
        self.request_1_org1.state = RequestState.COMPLETE
        self.request_1_org1.save()

        # Request 5 Target another service - Approval NOT USED
        self.request_5_team2org2.operation = self.operation_create_2
        self.request_5_team2org2.save()

        request_not_affected = Request.objects.filter(
            id__in=[
                self.request_1_org1.id,
                # self.request_2_team1org2.id,
                # self.request_3_team1org2.id,
                # self.request_4_team2org2.id,
                self.request_5_team2org2.id,
                # self.request_6_org2.id,
                # self.request_7_team1org3.id,
                # self.request_8_org3.id,
            ]
        ).all()
        request_affected = Request.objects.filter(
            id__in=[
                # self.request_1_org1.id,
                self.request_2_team1org2.id,
                self.request_3_team1org2.id,
                self.request_4_team2org2.id,
                # self.request_5_team2org2.id,
                self.request_6_org2.id,
                self.request_7_team1org3.id,
                self.request_8_org3.id,
            ]
        ).all()

        # No workflow set
        # Org        |  1   |  2   |  2   |  2   |  2   |  2   |  3   |  3   |
        # Team       | None |  1   |  1   |  2   |  2   | None |  1   | None |
        # Request ID |  1   |  2   |  3   |  4   |  5   |  6   |  7   |  8   |
        # -----------|------|------|------|------|------|------|------|------|
        # WF ID      | None | None | None | None | None | None | None | None |
        self.assertRequestDontUseWorkflow(Request.objects.all())

        # Create workflow for all
        wf_for_all = self._create_approval_for_all()

        self.assertQuerysetEqualID(request_affected, wf_for_all._get_all_requests_that_should_use_workflow())

        wf_for_all.reset_all_approval_workflow_state()
        # Org        |  1   |  2   |  2   |  2   |  2   |  2   |  3   |  3   |
        # Team       | None |  1   |  1   |  2   |  2   | None |  1   | None |
        # Request ID |  1   |  2   |  3   |  4   |  5   |  6   |  7   |  8   |
        # -----------|------|------|------|------|------|------|------|------|
        # WF ID      | None |  1   |  1   |  1   | None |  1   |  1   |  1   |
        self.assertRequestDontUseWorkflow(request_not_affected.all())
        self.assertRequestUseWorkflow(request_affected, wf_for_all)

        wf_for_all.delete()
        # Org        |  1   |  2   |  2   |  2   |  2   |  2   |  3   |  3   |
        # Team       | None |  1   |  1   |  2   |  2   | None |  1   | None |
        # Request ID |  1   |  2   |  3   |  4   |  5   |  6   |  7   |  8   |
        # -----------|------|------|------|------|------|------|------|------|
        # WF ID      | None | None | None | None | None | None | None | None |

        self.assertRequestDontUseWorkflow(Request.objects.all())

    def test_scenario2(self):

        # Scenario: setup a workflow for all + a workflow for Org 2

        request_of_org2 = Request.objects.filter(
            id__in=[
                # self.request_1_org1.id,
                self.request_2_team1org2.id,
                self.request_3_team1org2.id,
                self.request_4_team2org2.id,
                self.request_5_team2org2.id,
                self.request_6_org2.id,
                # self.request_7_team1org3.id,
                # self.request_8_org3.id,
            ]
        ).all()
        other_requests = Request.objects.filter(
            id__in=[
                self.request_1_org1.id,
                # self.request_2_team1org2.id,
                # self.request_3_team1org2.id,
                # self.request_4_team2org2.id,
                # self.request_5_team2org2.id,
                # self.request_6_org2.id,
                self.request_7_team1org3.id,
                self.request_8_org3.id,
            ]
        ).all()

        # Workflow for all
        wf_for_all = self._create_approval_for_all()

        self.assertQuerysetEqualID(Request.objects.all(), wf_for_all._get_all_requests_that_should_use_workflow())

        wf_for_all.reset_all_approval_workflow_state()
        # Org        |  1   |  2   |  2   |  2   |  2   |  2   |  3   |  3   |
        # Team       | None |  1   |  1   |  2   |  2   | None |  1   | None |
        # Request ID |  1   |  2   |  3   |  4   |  5   |  6   |  7   |  8   |
        # -----------|------|------|------|------|------|------|------|------|
        # WF ID      |  1   |  1   |  1   |  1   |  1   |  1   |  1   |  1   |
        self.assertRequestUseWorkflow(Request.objects.all(), wf_for_all)

        # Workflow for org2
        wf_for_org2 = self._create_approval_for_org2()

        self.assertQuerysetEqualID(other_requests.all(), wf_for_all._get_all_requests_that_should_use_workflow())
        self.assertQuerysetEqualID(request_of_org2.all(), wf_for_org2._get_all_requests_that_should_use_workflow())

        wf_for_org2.reset_all_approval_workflow_state()
        # Org        |  1   |  2   |  2   |  2   |  2   |  2   |  3   |  3   |
        # Team       | None |  1   |  1   |  2   |  2   | None |  1   | None |
        # Request ID |  1   |  2   |  3   |  4   |  5   |  6   |  7   |  8   |
        # -----------|------|------|------|------|------|------|------|------|
        # WF ID      |  1   |  2   |  2   |  2   |  2   |  2   |  1   |  1   |
        self.assertRequestUseWorkflow(other_requests.all(), wf_for_all)
        self.assertRequestUseWorkflow(request_of_org2.all(), wf_for_org2)

        # Delete workflow 2
        wf_for_org2.delete()
        wf_for_all.reset_all_approval_workflow_state()
        # Org        |  1   |  2   |  2   |  2   |  2   |  2   |  3   |  3   |
        # Team       | None |  1   |  1   |  2   |  2   | None |  1   | None |
        # Request ID |  1   |  2   |  3   |  4   |  5   |  6   |  7   |  8   |
        # -----------|------|------|------|------|------|------|------|------|
        # WF ID      |  1   |  1   |  1   |  1   |  1   |  1   |  1   |  1   |
        self.assertRequestUseWorkflow(Request.objects.all(), wf_for_all)

    def test_scenario3(self):

        # Scenario: setup a workflow for all + a workflow for Org 2 + workflow for Org2 - Team 1
        request_of_org2 = Request.objects.filter(
            id__in=[
                # self.request_1_org1.id,
                # self.request_2_team1org2.id,
                # self.request_3_team1org2.id,
                self.request_4_team2org2.id,
                self.request_5_team2org2.id,
                self.request_6_org2.id,
                # self.request_7_team1org3.id,
                # self.request_8_org3.id,
            ]
        ).all()

        request_of_org2_team1 = Request.objects.filter(
            id__in=[
                # self.request_1_org1.id,
                self.request_2_team1org2.id,
                self.request_3_team1org2.id,
                # self.request_4_team2org2.id,
                # self.request_5_team2org2.id,
                # self.request_6_org2.id,
                # self.request_7_team1org3.id,
                # self.request_8_org3.id,
            ]
        ).all()

        other_requests = Request.objects.filter(
            id__in=[
                self.request_1_org1.id,
                # self.request_2_team1org2.id,
                # self.request_3_team1org2.id,
                # self.request_4_team2org2.id,
                # self.request_5_team2org2.id,
                # self.request_6_org2.id,
                self.request_7_team1org3.id,
                self.request_8_org3.id,
            ]
        ).all()

        # Workflow for all
        wf_for_all = self._create_approval_for_all()

        self.assertQuerysetEqualID(Request.objects.all(), wf_for_all._get_all_requests_that_should_use_workflow())

        wf_for_all.reset_all_approval_workflow_state()
        # Org        |  1   |  2   |  2   |  2   |  2   |  2   |  3   |  3   |
        # Team       | None |  1   |  1   |  2   |  2   | None |  1   | None |
        # Request ID |  1   |  2   |  3   |  4   |  5   |  6   |  7   |  8   |
        # -----------|------|------|------|------|------|------|------|------|
        # WF ID      |  1   |  1   |  1   |  1   |  1   |  1   |  1   |  1   |

        # Workflow for org2
        wf_for_org2 = self._create_approval_for_org2()

        self.assertQuerysetEqualID(other_requests, wf_for_all._get_all_requests_that_should_use_workflow())
        self.assertQuerysetEqualID(request_of_org2 | request_of_org2_team1,
                                   wf_for_org2._get_all_requests_that_should_use_workflow())

        wf_for_org2.reset_all_approval_workflow_state()
        # Org        |  1   |  2   |  2   |  2   |  2   |  2   |  3   |  3   |
        # Team       | None |  1   |  1   |  2   |  2   | None |  1   | None |
        # Request ID |  1   |  2   |  3   |  4   |  5   |  6   |  7   |  8   |
        # -----------|------|------|------|------|------|------|------|------|
        # WF ID      |  1   |  2   |  2   |  2   |  2   |  2   |  1   |  1   |

        # Workflow for org2 - team1
        wf_for_org2_team1 = self._create_approval_for_org2_team1()

        self.assertQuerysetEqualID(other_requests, wf_for_all._get_all_requests_that_should_use_workflow())
        self.assertQuerysetEqualID(request_of_org2, wf_for_org2._get_all_requests_that_should_use_workflow())
        self.assertQuerysetEqualID(request_of_org2_team1, wf_for_org2_team1._get_all_requests_that_should_use_workflow())

        wf_for_org2_team1.reset_all_approval_workflow_state()
        # Org        |  1   |  2   |  2   |  2   |  2   |  2   |  3   |  3   |
        # Team       | None |  1   |  1   |  2   |  2   | None |  1   | None |
        # Request ID |  1   |  2   |  3   |  4   |  5   |  6   |  7   |  8   |
        # -----------|------|------|------|------|------|------|------|------|
        # WF ID      |  1   |  3   |  3   |  2   |  2   |  2   |  1   |  1   |

        self.assertQuerysetEqualID(request_of_org2_team1.all(), wf_for_org2_team1._get_request_using_workflow())
        self.assertQuerysetEqualID(request_of_org2.all(), wf_for_org2._get_request_using_workflow())
        self.assertQuerysetEqualID(other_requests.all(), wf_for_all._get_request_using_workflow())

        # Delete workflow 2
        wf_for_org2.delete()
        # Org        |  1   |  2   |  2   |  2   |  2   |  2   |  3   |  3   |
        # Team       | None |  1   |  1   |  2   |  2   | None |  1   | None |
        # Request ID |  1   |  2   |  3   |  4   |  5   |  6   |  7   |  8   |
        # -----------|------|------|------|------|------|------|------|------|
        # WF ID      |  1   |  3   |  3   | None | None | None |  1   |  1   |
        self.assertRequestDontUseWorkflow(request_of_org2.all())
        wf_for_all.reset_all_approval_workflow_state()

        # Org        |  1   |  2   |  2   |  2   |  2   |  2   |  3   |  3   |
        # Team       | None |  1   |  1   |  2   |  2   | None |  1   | None |
        # Request ID |  1   |  2   |  3   |  4   |  5   |  6   |  7   |  8   |
        # -----------|------|------|------|------|------|------|------|------|
        # WF ID      |  1   |  3   |  3   |  1   |  1   |  1   |  1   |  1   |

        # Everyone use wf_for_all except org2 - Team 1
        self.assertQuerysetEqualID(request_of_org2.all() | other_requests, wf_for_all._get_request_using_workflow())

        self.assertRequestUseWorkflow(request_of_org2_team1.all(), wf_for_org2_team1)
        self.assertRequestUseWorkflow(request_of_org2.all(), wf_for_all)
        self.assertRequestUseWorkflow(other_requests.all(), wf_for_all)

        # Delete workflow for all
        wf_for_all.delete()
        # Org        |  1   |  2   |  2   |  2   |  2   |  2   |  3   |  3   |
        # Team       | None |  1   |  1   |  2   |  2   | None |  1   | None |
        # Request ID |  1   |  2   |  3   |  4   |  5   |  6   |  7   |  8   |
        # -----------|------|------|------|------|------|------|------|------|
        # WF ID      | None |  3   |  3   |  2   |  2   |  2   | None | None |
        self.assertRequestUseWorkflow(request_of_org2_team1.all(), wf_for_org2_team1)
        self.assertRequestDontUseWorkflow(request_of_org2.all())
        self.assertRequestDontUseWorkflow(other_requests.all())

    def test_scenario4(self):

        # Scenario: setup a workflow for all + a workflow for Org 2 + workflow for Org2 - Team 1 then remove workflow
        request_of_org2 = Request.objects.filter(
            id__in=[
                # self.request_1_org1.id,
                # self.request_2_team1org2.id,
                # self.request_3_team1org2.id,
                self.request_4_team2org2.id,
                self.request_5_team2org2.id,
                self.request_6_org2.id,
                # self.request_7_team1org3.id,
                # self.request_8_org3.id,
            ]
        ).all()

        request_of_org2_team1 = Request.objects.filter(
            id__in=[
                # self.request_1_org1.id,
                self.request_2_team1org2.id,
                self.request_3_team1org2.id,
                # self.request_4_team2org2.id,
                # self.request_5_team2org2.id,
                # self.request_6_org2.id,
                # self.request_7_team1org3.id,
                # self.request_8_org3.id,
            ]
        ).all()

        other_requests = Request.objects.filter(
            id__in=[
                self.request_1_org1.id,
                # self.request_2_team1org2.id,
                # self.request_3_team1org2.id,
                # self.request_4_team2org2.id,
                # self.request_5_team2org2.id,
                # self.request_6_org2.id,
                self.request_7_team1org3.id,
                self.request_8_org3.id,
            ]
        ).all()
        # Workflow for all
        wf_for_all = self._create_approval_for_all()
        wf_for_all.reset_all_approval_workflow_state()

        # Workflow for org2
        wf_for_org2 = self._create_approval_for_org2()
        wf_for_org2.reset_all_approval_workflow_state()

        # Workflow for org2 - team1
        wf_for_org2_team1 = self._create_approval_for_org2_team1()
        wf_for_org2_team1.reset_all_approval_workflow_state()

        # Org        |  1   |  2   |  2   |  2   |  2   |  2   |  3   |  3   |
        # Team       | None |  1   |  1   |  2   |  2   | None |  1   | None |
        # Request ID |  1   |  2   |  3   |  4   |  5   |  6   |  7   |  8   |
        # -----------|------|------|------|------|------|------|------|------|
        # WF ID      |  1   |  3   |  3   |  2   |  2   |  2   |  1   |  1   |

        self.assertQuerysetEqualID(other_requests.all(), wf_for_all._get_request_using_workflow())
        self.assertQuerysetEqualID(request_of_org2.all(), wf_for_org2._get_request_using_workflow())
        self.assertQuerysetEqualID(request_of_org2_team1.all(), wf_for_org2_team1._get_request_using_workflow())

        # Delete workflow for all
        wf_for_all.delete()
        # Org        |  1   |  2   |  2   |  2   |  2   |  2   |  3   |  3   |
        # Team       | None |  1   |  1   |  2   |  2   | None |  1   | None |
        # Request ID |  1   |  2   |  3   |  4   |  5   |  6   |  7   |  8   |
        # -----------|------|------|------|------|------|------|------|------|
        # WF ID      | None |  3   |  3   |  2   |  2   |  2   | None | None |

        self.assertRequestDontUseWorkflow(other_requests.all())
        self.assertRequestUseWorkflow(request_of_org2.all(), wf_for_org2)
        self.assertRequestUseWorkflow(request_of_org2_team1.all(), wf_for_org2_team1)

        # Delete workflow for org2
        wf_for_org2.delete()
        # Org        |  1   |  2   |  2   |  2   |  2   |  2   |  3   |  3   |
        # Team       | None |  1   |  1   |  2   |  2   | None |  1   | None |
        # Request ID |  1   |  2   |  3   |  4   |  5   |  6   |  7   |  8   |
        # -----------|------|------|------|------|------|------|------|------|
        # WF ID      | None |  3   |  3   | None | None | None | None | None |
        self.assertRequestDontUseWorkflow(other_requests.all())
        self.assertRequestDontUseWorkflow(request_of_org2.all())
        self.assertRequestUseWorkflow(request_of_org2_team1.all(), wf_for_org2_team1)
