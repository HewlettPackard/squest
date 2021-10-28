from rest_framework import serializers

from profiles.models import BillingGroup


class BillingGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingGroup
        fields = '__all__'
