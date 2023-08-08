from profiles.models.squest_permission import Permission
from django.core.exceptions import ValidationError
from django.forms import ModelMultipleChoiceField, HiddenInput
from django.urls import reverse

from Squest.utils.squest_model_form import SquestModelForm
from service_catalog.models import ApprovalStep, SurveyField


class ApprovalStepForm(SquestModelForm):
    readable_fields = ModelMultipleChoiceField(label="Readable fields",
                                               required=False,
                                               queryset=SurveyField.objects.none())

    editable_fields = ModelMultipleChoiceField(label="Editable fields",
                                               required=False,
                                               queryset=SurveyField.objects.none())

    class Meta:
        model = ApprovalStep
        fields = ['name', 'permission', 'readable_fields', 'editable_fields', 'approval_workflow']

    def __init__(self, *args, **kwargs):
        self.approval_workflow = kwargs.pop('approval_workflow', None)
        super().__init__(*args, **kwargs)
        self.fields["readable_fields"].queryset = self.approval_workflow.operation.survey_fields.all()
        self.fields["editable_fields"].queryset = self.approval_workflow.operation.survey_fields.all()

        self.fields['approval_workflow'].widget = HiddenInput()
        self.fields['approval_workflow'].initial = self.approval_workflow.id

        self.fields['permission'].help_text = f"Create a <a href='{reverse('profiles:approvalstep_permission_create')}'>permission</a>"
        default_perm = Permission.objects.get(codename="can_approve_approvalstep")
        self.fields['permission'].initial = (default_perm.id, default_perm.name)

    def clean(self):
        cleaned_data = super().clean()
        readable_fields = cleaned_data.get("readable_fields")
        editable_fields = cleaned_data.get("editable_fields")
        field_in_both_list = [field for field in readable_fields if field in editable_fields]
        if field_in_both_list:
            raise ValidationError({"readable_fields": f"A field cannot be declared as read and write"})
