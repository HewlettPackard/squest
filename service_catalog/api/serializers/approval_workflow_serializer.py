from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from service_catalog.models import ApprovalWorkflow


class ApprovalWorkflowSerializer(ModelSerializer):
    class Meta:
        model = ApprovalWorkflow
        fields = ['id', 'name', 'operation', 'scopes']
        read_only_fields = ['id']

    def validate(self, data):
        super(ApprovalWorkflowSerializer, self).validate(data)
        operation = data.get("operation")
        scopes = data.get("scopes")
        # check that selected scopes are not already in use by another approval workflow for the selected operation
        for scope in scopes:
            if scope.approval_workflows.filter(operation=operation).exists():
                raise ValidationError({"scopes": f"The scope {scope} has already an approval workflow "
                                                 f"based on this operation"})
        return data
