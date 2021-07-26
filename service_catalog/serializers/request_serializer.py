from rest_framework import serializers

from service_catalog.models import Request
from service_catalog.serializers.instance_serializer import InstanceSerializer


class RequestSerializer(serializers.ModelSerializer):

    instance = InstanceSerializer()

    class Meta:
        model = Request
        fields = ['id', 'state', 'instance', 'operation']
        read_only_fields = ['instance', 'state']
