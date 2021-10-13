from rest_framework import serializers

from resource_tracker.models import ResourceGroupAttributeDefinition


class ResourceGroupAttributeDefinitionSerializerRead(serializers.ModelSerializer):
    class Meta:
        model = ResourceGroupAttributeDefinition
        fields = ["id", "resource_group_definition", "name", "consume_from", "produce_for", "help_text"]
        read_only_fields = ["resource_group_definition"]


class ResourceGroupAttributeDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceGroupAttributeDefinition
        fields = ["id", "resource_group_definition", "name", "consume_from", "produce_for", "help_text"]


class AttributeCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    value = serializers.IntegerField()

    def validate_name(self, value):
        """Chek that this name is one the the attribute"""
        resource_group = self.context.get('resource_group')
        try:
            ResourceGroupAttributeDefinition.objects.get(name=value, resource_group_definition=resource_group)
            return value
        except ResourceGroupAttributeDefinition.DoesNotExist:
            raise serializers.ValidationError(f"'{value}' is not a valid attribute of the resource "
                                              f"group '{resource_group.name}'")
