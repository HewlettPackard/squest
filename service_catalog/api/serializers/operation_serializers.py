from rest_framework.serializers import ModelSerializer, ValidationError

from service_catalog.models import Operation


class OperationSerializer(ModelSerializer):
    class Meta:
        model = Operation
        fields = '__all__'
        read_only = True

    def validate_extra_vars(self, value):
        if value is None or not isinstance(value, dict):
            raise ValidationError("Please enter a valid JSON. Empty value is {} for JSON.")
        return value
