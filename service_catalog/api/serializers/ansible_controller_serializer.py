from rest_framework.serializers import ModelSerializer, ValidationError

from service_catalog.models import AnsibleController


class AnsibleControllerSerializer(ModelSerializer):
    class Meta:
        model = AnsibleController
        exclude = ('token',)


class AnsibleControllerCreateSerializer(ModelSerializer):
    class Meta:
        model = AnsibleController
        fields = '__all__'

    def validate_extra_vars(self, value):
        if value is None or not isinstance(value, dict):
            raise ValidationError("Please enter a valid JSON. Empty value is {} for JSON.")
        return value
