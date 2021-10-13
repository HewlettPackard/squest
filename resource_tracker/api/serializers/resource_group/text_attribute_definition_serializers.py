from rest_framework import serializers

from resource_tracker.models import ResourceGroupTextAttributeDefinition


class ResourceGroupTextAttributeDefinitionSerializerRead(serializers.ModelSerializer):
    class Meta:
        model = ResourceGroupTextAttributeDefinition
        fields = ["id", "resource_group_definition", "name", "help_text"]
        read_only_fields = ["resource_group_definition"]


class ResourceGroupTextAttributeDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceGroupTextAttributeDefinition
        fields = ["id", "resource_group_definition", "name", "help_text"]


class TextAttributeCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    value = serializers.CharField(max_length=500)

    def validate_name(self, value):
        """Chek that this name is one the the text attribute"""
        resource_group = self.context.get('resource_group')
        try:
            ResourceGroupTextAttributeDefinition.objects.get(name=value, resource_group_definition=resource_group)
            return value
        except ResourceGroupTextAttributeDefinition.DoesNotExist:
            raise serializers.ValidationError(f"'{value}' is not a valid text attribute of the resource "
                                              f"group '{resource_group.name}'")
