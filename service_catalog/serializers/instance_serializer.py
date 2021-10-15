from rest_framework import serializers

from resource_tracker.api.serializers.resource_group.resource_serializers import ResourceSerializer
from service_catalog.models import Instance, InstanceState


class InstanceSerializer(serializers.ModelSerializer):
    state = serializers.ChoiceField(choices=InstanceState.choices)
    resources = ResourceSerializer(many=True, read_only=True)

    class Meta:
        model = Instance
        fields = '__all__'
