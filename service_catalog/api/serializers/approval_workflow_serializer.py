from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from service_catalog.models import ApprovalWorkflow


class ApprovalWorkflowSerializer(ModelSerializer):
    class Meta:
        model = ApprovalWorkflow
        fields = ['id', 'enabled', 'name', 'operation', 'scopes']
        read_only_fields = ['id']

    def validate(self, data):
        super(ApprovalWorkflowSerializer, self).validate(data)
        operation = self.instance.operation if self.instance is not None else None
        operation = data.get("operation") if 'operation' in data.keys() else operation
        scopes = self.instance.scopes.all() if self.instance is not None else list()
        scopes = data.get("scopes") if 'scopes' in data.keys() else scopes
        # check that selected scopes are not already in use by another approval workflow for the selected operation
        exclude_id = self.instance.id if self.instance else None
        if len(scopes) == 0:
            if ApprovalWorkflow.objects.filter(enabled=True, operation=operation, scopes__isnull=True).exclude(
                    id=exclude_id).exists():
                raise ValidationError({"scopes": f"An approval workflow for all scopes already exists"})
        for scope in scopes:
            if scope.approval_workflows.filter(operation=operation).exclude(id=exclude_id).exists():
                raise ValidationError({"scopes": f"The scope {scope} has already an approval workflow "
                                                 f"based on this operation"})
        return data


class ApprovalWorkflowSerializerEdit(ApprovalWorkflowSerializer):
    class Meta:
        model = ApprovalWorkflow
        fields = ['id', 'enabled', 'name', 'operation', 'scopes']
        read_only_fields = ['id', "operation"]
