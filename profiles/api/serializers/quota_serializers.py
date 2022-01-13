from rest_framework import serializers

from profiles.models import Quota


class QuotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quota
        fields = '__all__'
