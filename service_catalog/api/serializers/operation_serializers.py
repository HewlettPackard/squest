from rest_framework.serializers import ModelSerializer, ValidationError

from service_catalog.models import Operation


class OperationSerializer(ModelSerializer):
    class Meta:
        model = Operation
        fields = '__all__'
        read_only_fields = ["service", ]

    def __init__(self, *args, **kwargs):
        self.service = kwargs['context'].get('service')
        super(OperationSerializer, self).__init__(*args, **kwargs)

    def validate_extra_vars(self, value):
        if value is None or not isinstance(value, dict):
            raise ValidationError("Please enter a valid JSON. Empty value is {} for JSON.")
        return value

    def create(self, validated_data):
        validated_data['service'] = self.service
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['service'] = self.service
        return super().update(instance, validated_data)
