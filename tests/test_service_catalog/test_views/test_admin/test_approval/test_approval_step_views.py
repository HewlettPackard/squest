import json

from django.urls import reverse

from service_catalog.models import ApprovalState
from tests.test_service_catalog.base_test_approval import BaseTestApproval


class TestApprovalStepViews(BaseTestApproval):

    def setUp(self):
        super(TestApprovalStepViews, self).setUp()

    def test_ajax_approval_step_position_update(self):
        self.assertEqual(self.test_approval_step_1.position, 0)
        self.assertEqual(self.test_approval_step_2.position, 1)

        for approval_state in self.test_request.approval_workflow_state.approval_step_states.all():
            approval_state.state = ApprovalState.APPROVED
            approval_state.save()

        url = reverse('service_catalog:ajax_approval_step_position_update')
        data = {
            "listStepToUpdate": json.dumps([{"id": self.test_approval_step_1.id, "position": 1},
                                            {"id": self.test_approval_step_2.id, "position": 0}])
        }
        response = self.client.post(url, data=data)
        self.assertEqual(202, response.status_code)
        self.test_approval_step_1.refresh_from_db()
        self.test_approval_step_2.refresh_from_db()
        self.assertEqual(self.test_approval_step_1.position, 1)
        self.assertEqual(self.test_approval_step_2.position, 0)
        # check reset
        for approval_state in self.test_request.approval_workflow_state.approval_step_states.all():
            self.assertEqual(approval_state.state, ApprovalState.PENDING)
