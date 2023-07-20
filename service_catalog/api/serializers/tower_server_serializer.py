from rest_framework.serializers import ModelSerializer, ValidationError

from service_catalog.models import TowerServer


class TowerServerSerializer(ModelSerializer):
    class Meta:
        model = TowerServer
        exclude = ('token',)


class TowerServerCreateSerializer(ModelSerializer):
    class Meta:
        model = TowerServer
        fields = '__all__'

    def validate_extra_vars(self, value):
        if value is None or not isinstance(value, dict):
            raise ValidationError("Please enter a valid JSON. Empty value is {} for JSON.")
        return value
