from rest_framework import serializers

from profiles.models import BillingGroup


class BillingGroupReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingGroup
        fields = ['id', 'name', 'user_set', 'quota_bindings']


class BillingGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingGroup
        fields = ['id', 'name', 'user_set']
        read_only_fields = ['id']


class BillingGroupInstanceReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingGroup
        fields = ['id', 'name', 'quota_bindings']
