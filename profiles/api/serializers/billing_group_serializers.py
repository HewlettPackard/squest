from rest_framework import serializers

from profiles.models import BillingGroup


class BillingGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingGroup
        fields = ['id', 'name', 'user_set', 'quota_bindings']


class BillingGroupWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingGroup
        fields = ['name', 'user_set']


class BillingGroupInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingGroup
        fields = ['id', 'name', 'quota_bindings']
