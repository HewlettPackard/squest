from rest_framework import serializers

from resource_tracker.models import ResourcePoolAttributeDefinition


class ResourcePoolAttributeDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourcePoolAttributeDefinition
        fields = ["id", "resource_pool", "name", "over_commitment_producers", "over_commitment_consumers"]


class ResourcePoolAttributeDefinitionSerializerRead(serializers.ModelSerializer):
    class Meta:
        model = ResourcePoolAttributeDefinition
        fields = ["id", "resource_pool", "name", "over_commitment_producers", "over_commitment_consumers"]
        read_only_fields = ["resource_pool"]
