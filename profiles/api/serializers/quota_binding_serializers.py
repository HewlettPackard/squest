from rest_framework import serializers

from profiles.models import QuotaBinding


class QuotaBindingReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotaBinding
        fields = '__all__'


class QuotaBindingSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotaBinding
        fields = ['billing_group', 'quota', 'limit']
