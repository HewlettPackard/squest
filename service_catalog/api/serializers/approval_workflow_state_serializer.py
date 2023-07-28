from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from service_catalog.api.serializers.approval_step_state_serializer import ApprovalStepStateSerializer
from service_catalog.models import ApprovalWorkflowState


class ApprovalWorkflowStateSerializer(ModelSerializer):
    approval_workflow = PrimaryKeyRelatedField(read_only=True)
    current_step = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ApprovalWorkflowState
        fields = ['id', 'approval_workflow', 'approval_step_states', 'current_step']

    def __init__(self, *args, **kwargs):
        super(ApprovalWorkflowStateSerializer, self).__init__(*args, **kwargs)
        self.fields["approval_step_states"] = ApprovalStepStateSerializer(many=True,
                                                                          user=self.context.get("user"))
