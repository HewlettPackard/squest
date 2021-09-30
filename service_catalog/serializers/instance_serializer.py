from rest_framework import serializers

from service_catalog.models import Instance, InstanceState


class InstanceSerializer(serializers.ModelSerializer):
    state = serializers.ChoiceField(choices=InstanceState.choices)

    class Meta:
        model = Instance
        fields = '__all__'
