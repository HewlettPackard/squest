from rest_framework.serializers import ModelSerializer, JSONField
from service_catalog.models import Service


class ServiceSerializer(ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'
        read_only = True


class AdminServiceSerializer(ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'
    extra_vars = JSONField(binary=True)

