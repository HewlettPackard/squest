from rest_framework import serializers

from service_catalog.models import Instance


class InstanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Instance
        fields = '__all__'
        read_only_fields = ['service', 'state']
