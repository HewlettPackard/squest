from rest_framework.exceptions import ValidationError
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from profiles.models import Permission
from service_catalog.models import ApprovalStep, TowerSurveyField

EXCLUDED_PERMISSION = ["add_approvalstep", "change_approvalstep", "delete_approvalstep", "list_approvalstep",
                       "view_approvalstep"]


class ApprovalStepSerializer(ModelSerializer):
    class Meta:
        model = ApprovalStep
        fields = ['id', 'approval_workflow', 'name', 'permission', 'readable_fields', 'editable_fields', 'auto_accept_condition']

    permission = PrimaryKeyRelatedField(queryset=Permission.objects.filter(content_type__app_label='service_catalog',
                                                                           content_type__model='approvalstep').exclude(codename__in=EXCLUDED_PERMISSION))
    readable_fields = PrimaryKeyRelatedField(many=True, queryset=TowerSurveyField.objects.all())
    editable_fields = PrimaryKeyRelatedField(many=True, queryset=TowerSurveyField.objects.all())

    def validate(self, data):
        approval_workflow = self.instance.approval_workflow if self.instance else None
        approval_workflow = data.get("approval_workflow") if "approval_workflow" in data.keys() else approval_workflow

        readable_fields = self.instance.readable_fields.all() if self.instance else None
        readable_fields = data.get("readable_fields") if "readable_fields" in data.keys() else readable_fields
        editable_fields = self.instance.editable_fields.all() if self.instance else None
        editable_fields = data.get("editable_fields") if "editable_fields" in data.keys() else editable_fields

        not_allowed_editable_fields = [field for field in editable_fields if
                                       field not in TowerSurveyField.objects.filter(
                                           operation=approval_workflow.operation)]
        not_allowed_readable_fields = [field for field in readable_fields if
                                       field not in TowerSurveyField.objects.filter(
                                           operation=approval_workflow.operation)]
        if not_allowed_editable_fields:
            raise ValidationError({"editable_fields": f"The field{'s' if len(not_allowed_editable_fields) > 1 else ''} {','.join(not_allowed_editable_fields)} {'are' if len(not_allowed_editable_fields) > 1 else 'is'} not a {approval_workflow.operation} fields"})
        if not_allowed_readable_fields:
            raise ValidationError({"readable_fields": f"The field{'s' if len(not_allowed_readable_fields) > 1 else ''} {','.join(not_allowed_readable_fields)} {'are' if len(not_allowed_readable_fields) > 1 else 'is'} not a {approval_workflow.operation} fields"})
        field_in_both_list = [field for field in readable_fields if field in editable_fields]
        if field_in_both_list:
            raise ValidationError({"readable_fields": f"A field cannot be declared as read and write"})
        return data


class ApprovalStepPositionSerializer(ModelSerializer):
    class Meta:
        model = ApprovalStep
        fields = ['position']
        read_only_fields = ['id']
