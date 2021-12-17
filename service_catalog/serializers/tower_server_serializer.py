from rest_framework import serializers
from service_catalog.models import TowerServer


class TowerServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TowerServer
        exclude = ('token',)


class TowerServerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TowerServer
        fields = '__all__'
