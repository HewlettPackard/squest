from copy import deepcopy

from rest_framework.exceptions import ValidationError
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from service_catalog.models import ApprovalStep, TowerSurveyField


class ApprovalStepSerializer(ModelSerializer):
    class Meta:
        model = ApprovalStep
        fields = ['id', 'name', 'permission', 'readable_fields', 'editable_fields']
        read_only_fields = ['id']

    readable_fields = PrimaryKeyRelatedField(many=True, queryset=TowerSurveyField.objects.none())
    editable_fields = PrimaryKeyRelatedField(many=True, queryset=TowerSurveyField.objects.none())

    def __init__(self, *args, **kwargs):
        from service_catalog.models import ApprovalWorkflow
        self.approval_workflow = ApprovalWorkflow.objects.get(id=kwargs['context'].get('approval_workflow_id'))
        super(ApprovalStepSerializer, self).__init__(*args, **kwargs)
        queryset = TowerSurveyField.objects.filter(operation=self.approval_workflow.operation)
        self.fields["editable_fields"].child_relation.queryset = queryset
        self.fields["readable_fields"].child_relation.queryset = queryset

    def create(self, validated_data):
        validated_data['approval_workflow'] = self.approval_workflow
        return super().create(validated_data)

    def validate(self, data):
        readable_fields = self.instance.readable_fields.all() if self.instance else None
        readable_fields = data.get("readable_fields") if "readable_fields" in data.keys() else readable_fields
        editable_fields = self.instance.editable_fields.all() if self.instance else None
        editable_fields = data.get("editable_fields") if "editable_fields" in data.keys() else editable_fields
        field_in_both_list = [field for field in readable_fields if field in editable_fields]
        if field_in_both_list:
            raise ValidationError({"readable_fields": f"A field cannot be declared as read and write"})
        return data


class ApprovalStepPositionSerializer(ModelSerializer):
    class Meta:
        model = ApprovalStep
        fields = ['position']
        read_only_fields = ['id']
