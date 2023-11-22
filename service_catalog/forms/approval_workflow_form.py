from django.core.exceptions import ValidationError

from Squest.utils.squest_model_form import SquestModelForm
from service_catalog.models import ApprovalWorkflow


class ApprovalWorkflowForm(SquestModelForm):
    class Meta:
        model = ApprovalWorkflow
        fields = ['name', 'operation', 'scopes', 'enabled']

    def clean(self):
        cleaned_data = super().clean()
        operation = cleaned_data.get("operation")
        scopes = cleaned_data.get("scopes")
        # check that selected scopes are not already in use by another approval workflow for the selected operation
        exclude_id = self.instance.id if self.instance else None
        if not scopes.exists():
            if ApprovalWorkflow.objects.filter(enabled=True, operation=operation, scopes__isnull=True).exclude(
                    id=exclude_id).exists():
                raise ValidationError({"scopes": f"An approval workflow for all scopes already exists"})
        for scope in scopes:
            if scope.approval_workflows.filter(operation=operation).exclude(id=exclude_id).exists():
                raise ValidationError({"scopes": f"The scope {scope} has already an approval workflow "
                                                 f"based on this operation"})


class ApprovalWorkflowFormEdit(ApprovalWorkflowForm):
    class Meta:
        model = ApprovalWorkflow
        fields = ['name', 'scopes', 'enabled']
