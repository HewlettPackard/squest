from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from service_catalog.models.tower_survey_field import TowerSurveyField


class TowerSurveyFieldSerializer(ModelSerializer):

    class Meta:
        model = TowerSurveyField
        fields = '__all__'
        read_only_fields = ('variable', 'operation', 'type', 'required', 'name', 'description', 'field_options')

    def validate(self, data):
        super().validate(data)
        field_type = self.instance.type if self.instance is not None else None
        attribute_definition = self.instance.attribute_definition if self.instance is not None else None
        attribute_definition = data.get("attribute_definition") if 'attribute_definition' in data.keys() else attribute_definition
        if attribute_definition and field_type != 'integer':
            raise ValidationError({"attribute_definition": f"Attribute definition must be linked to an integer field"})
        return data
