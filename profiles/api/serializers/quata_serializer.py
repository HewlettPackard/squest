from rest_framework import serializers

from profiles.models import Quota


class QuotaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Quota
        fields = ["id", "scope", "attribute_definition", "limit"]
        read_only_fields = ['id']


class QuotaReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Quota
        fields = ["id", "attribute_definition", "limit"]
        read_only_fields = ['id']
