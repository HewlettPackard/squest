from django.core.exceptions import ValidationError

from Squest.utils.squest_model_form import SquestModelForm
from service_catalog.models import ApprovalWorkflow


class ApprovalWorkflowForm(SquestModelForm):

    class Meta:
        model = ApprovalWorkflow
        fields = ['name', 'operation', 'scopes']

    def clean(self):
        cleaned_data = super().clean()
        operation = cleaned_data.get("operation")
        scopes = cleaned_data.get("scopes")
        # check that selected scopes are not already in use by another approval workflow for the selected operation
        for scope in scopes:
            if scope.approval_workflows.filter(operation=operation).exists():
                raise ValidationError({"scopes": f"The scope {scope} has already an approval workflow "
                                                 f"based on this operation"})
