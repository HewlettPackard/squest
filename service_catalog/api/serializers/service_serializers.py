from rest_framework.serializers import ModelSerializer
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

