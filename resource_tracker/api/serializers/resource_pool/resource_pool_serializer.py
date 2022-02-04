from rest_framework import serializers
from taggit.serializers import TaggitSerializer, TagListSerializerField

from resource_tracker.api.serializers.resource_pool.attribute_definition_serializers import \
    ResourcePoolAttributeDefinitionSerializerRead, ResourcePoolAttributeDefinitionSerializer
from resource_tracker.models import ResourcePool


class ResourcePoolSerializer(TaggitSerializer, serializers.ModelSerializer):
    attribute_definitions = ResourcePoolAttributeDefinitionSerializerRead(many=True)
    tags = TagListSerializerField()

    class Meta:
        model = ResourcePool
        fields = ["id", "name", "attribute_definitions", "tags"]

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        attribute_definitions_data = validated_data.pop('attribute_definitions', [])
        resource_pool = ResourcePool.objects.create(**validated_data)
        resource_pool.tags.set(tags)
        for attribute_definition in attribute_definitions_data:
            resource_pool.add_attribute_definition(**attribute_definition)
        return resource_pool


class ResourcePoolSerializerRead(TaggitSerializer, serializers.ModelSerializer):
    attribute_definitions = ResourcePoolAttributeDefinitionSerializer(many=True, read_only=True)
    tags = TagListSerializerField()

    class Meta:
        model = ResourcePool
        fields = ["id", "name", "attribute_definitions", "tags"]
