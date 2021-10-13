from rest_framework import serializers
from taggit.serializers import TaggitSerializer, TagListSerializerField

from resource_tracker.api.serializers.resource_group.attribute_definition_serializers import \
    ResourceGroupAttributeDefinitionSerializerRead
from resource_tracker.api.serializers.resource_group.text_attribute_definition_serializers import \
    ResourceGroupTextAttributeDefinitionSerializerRead
from resource_tracker.models import ResourceGroup


class ResourceGroupSerializerRead(TaggitSerializer, serializers.ModelSerializer):
    attribute_definitions = ResourceGroupTextAttributeDefinitionSerializerRead(many=True, read_only=True)
    text_attribute_definitions = ResourceGroupTextAttributeDefinitionSerializerRead(many=True, read_only=True)
    tags = TagListSerializerField()

    class Meta:
        model = ResourceGroup
        fields = ["id", "name", "attribute_definitions", "text_attribute_definitions", "tags"]


class ResourceGroupSerializer(TaggitSerializer, serializers.ModelSerializer):
    attribute_definitions = ResourceGroupAttributeDefinitionSerializerRead(many=True)
    text_attribute_definitions = ResourceGroupAttributeDefinitionSerializerRead(many=True)
    tags = TagListSerializerField()

    class Meta:
        model = ResourceGroup
        fields = ["id", "name", "attribute_definitions", "text_attribute_definitions", "tags"]

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        attribute_definitions_data = validated_data.pop('attribute_definitions')
        text_attribute_definitions_data = validated_data.pop('text_attribute_definitions')
        resource_group = ResourceGroup.objects.create(**validated_data)
        resource_group.tags.set(*tags)
        for attribute_definition in attribute_definitions_data:
            resource_group.add_attribute_definition(**attribute_definition)
        for text_attribute_definition in text_attribute_definitions_data:
            resource_group.add_text_attribute_definition(**text_attribute_definition)
        return resource_group
