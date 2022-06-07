from rest_framework.fields import IntegerField
from rest_framework.serializers import ModelSerializer
from service_catalog.models.approval_step import ApprovalStep


class ApprovalStepSerializer(ModelSerializer):
    class Meta:
        model = ApprovalStep
        fields = '__all__'
        read_only_fields = ('id', 'next', 'approval_workflow', 'position')

    previous_id = IntegerField(write_only=True, required=False)
