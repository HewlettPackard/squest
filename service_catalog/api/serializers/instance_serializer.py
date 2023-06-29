from rest_framework import serializers

from profiles.api.serializers import UserSerializer, ScopeSerializer
from resource_tracker_v2.api.serializers.resource_serializer import ResourceSerializer
from service_catalog.models import Instance, InstanceState


class InstanceReadSerializer(serializers.ModelSerializer):
    state = serializers.ChoiceField(choices=InstanceState.choices)
    resources = ResourceSerializer(many=True, read_only=True)
    requester = UserSerializer(read_only=True)
    quota_scope = ScopeSerializer(read_only=True)

    class Meta:
        model = Instance
        fields = '__all__'


class RestrictedInstanceReadSerializer(InstanceReadSerializer):
    requester = UserSerializer(read_only=True)

    class Meta:
        model = Instance
        exclude = ["spec"]


class InstanceSerializer(serializers.ModelSerializer):
    state = serializers.ChoiceField(choices=InstanceState.choices)
    resources = ResourceSerializer(many=True, read_only=True)
    quota_scope = ScopeSerializer(read_only=True)
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
