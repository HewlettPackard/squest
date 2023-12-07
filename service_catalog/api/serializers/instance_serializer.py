from rest_framework import serializers

from profiles.api.serializers import ScopeSerializerNested, UserSerializerNested
from resource_tracker_v2.api.serializers.resource_serializer import ResourceSerializer
from service_catalog.models import Instance, InstanceState


class InstanceReadSerializer(serializers.ModelSerializer):
    state = serializers.ChoiceField(choices=InstanceState.choices)
    resources = ResourceSerializer(many=True, read_only=True)
    requester = UserSerializerNested()
    quota_scope = ScopeSerializerNested(read_only=True)

    class Meta:
        model = Instance
        fields = '__all__'


class RestrictedInstanceReadSerializer(InstanceReadSerializer):
    requester = UserSerializerNested(read_only=True)

    class Meta:
        model = Instance
        exclude = ["spec"]


class InstanceSerializer(serializers.ModelSerializer):
    state = serializers.ChoiceField(choices=InstanceState.choices)
    resources = ResourceSerializer(many=True, read_only=True)

    class Meta:
        model = Instance
        fields = '__all__'


class InstanceSerializerUserSpec(serializers.ModelSerializer):
    class Meta:
        model = Instance
        fields = ('user_spec',)


class InstanceSerializerSpec(serializers.ModelSerializer):
    class Meta:
        model = Instance
        fields = ('spec',)
