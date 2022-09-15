from rest_framework.serializers import ModelSerializer, JSONField
from service_catalog.models import TowerServer


class TowerServerSerializer(ModelSerializer):
    class Meta:
        model = TowerServer
        exclude = ('token',)


class TowerServerCreateSerializer(ModelSerializer):
    class Meta:
        model = TowerServer
        fields = '__all__'

    extra_vars = JSONField(binary=True)
