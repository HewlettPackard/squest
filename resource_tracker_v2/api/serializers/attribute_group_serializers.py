from rest_framework import serializers

from resource_tracker_v2.models import AttributeGroup


class AttributeGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = AttributeGroup
        fields = ["id", "name", "description"]
