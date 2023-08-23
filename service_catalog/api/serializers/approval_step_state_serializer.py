from rest_framework.serializers import ModelSerializer, Field

from service_catalog.models import ApprovalStepState


class ApprovalStepStateSerializer(ModelSerializer):

    class Meta:
        model = ApprovalStepState
        fields = ['id', 'approval_step', 'state', 'updated_by', 'date_updated', 'fill_in_survey']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(ApprovalStepStateSerializer, self).__init__(*args, **kwargs)

    def to_representation(self, current_step):
        representation = super().to_representation(current_step)
        if not self.user.has_perm(current_step.approval_step.permission.permission_str,
                                  current_step.approval_workflow_state.request):
            representation.pop("fill_in_survey")
        return representation
