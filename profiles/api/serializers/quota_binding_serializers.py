from rest_framework import serializers

from profiles.models import QuotaBinding


class QuotaBindingSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotaBinding
        fields = '__all__'


class QuotaBindingWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotaBinding
        fields = ['billing_group', 'quota', 'limit']
