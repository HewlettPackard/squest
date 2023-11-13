from rest_framework import serializers

from resource_tracker_v2.models import AttributeDefinition


class AttributeDefinitionSerializer(serializers.ModelSerializer):

    class Meta:
        model = AttributeDefinition
        fields = ["id", "name", "description", "attribute_group"]
