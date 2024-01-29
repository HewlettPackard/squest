from profiles.models import Scope
from service_catalog.models import ApprovalWorkflow, Request
from tests.setup import SetupRequest
from tests.utils import TransactionTestUtils

from django.db.models.query import QuerySet


class TestApprovalWorkflowReset(TransactionTestUtils, SetupRequest):

    def setUp(self):
        SetupRequest.setUp(self)

    def _create_approval(self, operation, scopes=None):
        if isinstance(scopes, Scope):
            scopes = [scopes]
        aw = ApprovalWorkflow.objects.create(
            name=f"AW - {operation} - {scopes}",
            operation=operation,
            enabled=True
        )
        if scopes:
            aw.scopes.set(scopes)
        return aw

    def test_get_workflows(self):
        # team1org2 -> no workflows
        self.assertQuerysetEqualID(self.team1org2.get_workflows(), ApprovalWorkflow.objects.none())

        # team1org2 -> workflow for all on operation_create1
        aw_for_all = self._create_approval(self.operation_create_1)
        self.assertQuerysetEqualID(self.team1org2.get_workflows(), ApprovalWorkflow.objects.filter(id=aw_for_all.id))

        # team1org2 -> workflow for org2 on operation_create1 ("All" overridden by org2)
        aw_for_org2 = self._create_approval(self.operation_create_1, self.org2)
        self.assertQuerysetEqualID(self.team1org2.get_workflows(), ApprovalWorkflow.objects.filter(id=aw_for_org2.id))

        # team1org2 -> workflow for team1org2 on operation_create1 ( org2 overridden by team1org2)
        aw_for_org2_team1 = self._create_approval(self.operation_create_1, self.team1org2)
        self.assertQuerysetEqualID(
            self.team1org2.get_workflows(),
            ApprovalWorkflow.objects.filter(id=aw_for_org2_team1.id)
        )

        # team1org2 -> workflow for team1org2 on operation_create1 ( org2 overridden by team1org2)
        # team1org2 -> +  workflow for all on operation_update1
        aw_for_all_update1 = self._create_approval(self.operation_update_1)
        self.assertQuerysetEqualID(self.team1org2.get_workflows(), ApprovalWorkflow.objects.filter(
            id__in=[aw_for_org2_team1.id, aw_for_all_update1.id]))
