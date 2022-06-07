from rest_framework import serializers
from service_catalog.models.approval_workflow import ApprovalWorkflow


class ApprovalWorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalWorkflow
        fields = '__all__'
        read_only_fields = ('id', 'entry_point')