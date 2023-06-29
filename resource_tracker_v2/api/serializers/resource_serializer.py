from rest_framework import serializers

from resource_tracker_v2.models import Resource, ResourceAttribute, AttributeDefinition, Transformer


class ResourceAttributeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="attribute_definition.name")

    class Meta:
        model = ResourceAttribute
        fields = ["value", "name"]


class ResourceAttributeCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    value = serializers.IntegerField()

    def validate_name(self, value):
        """
        Check that this name is one of the attribute
        """
        resource_group = self.context.get('resource_group')
        try:
            Transformer.objects.filter(resource_group=resource_group, attribute_definition__name=value)
            return value
        except AttributeDefinition.DoesNotExist:
            raise serializers.ValidationError(f"'{value}' is not a valid attribute of the resource "
                                              f"group '{resource_group.name}'")


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ["id", "resource_group", "name", "service_catalog_instance",
                  "resource_attributes", "is_deleted_on_instance_deletion"]
        read_only_fields = ["resource_group"]

    resource_attributes = ResourceAttributeSerializer(many=True)

    def validate_resource_attributes(self, attributes):
        resource_group = self.context["resource_group"]
        # check attribute exist
        seen = set()
        for attribute in attributes:
            attribute_name = attribute["attribute_definition"].get('name')
            # get the attribute
            if not AttributeDefinition.objects.filter(name=attribute_name).exists():
                raise serializers.ValidationError(f"Attribute does not exist '{attribute_name}'")
            attribute_def = AttributeDefinition.objects.get(name=attribute_name)
            # check attribute is linked to the target resource group
            if not Transformer.objects.filter(attribute_definition=attribute_def,
                                              resource_group=resource_group).exists():
                raise serializers.ValidationError(
                    f"Attribute '{attribute_name}' not linked to resource group '{resource_group}'")
            # check for duplicate
            if attribute_name not in seen:
                seen.add(attribute_name)
            else:
                raise serializers.ValidationError(f"Duplicate attribute '{attribute_name}'")
        return attributes

    def update(self, instance, validated_data):
        resource_attributes = validated_data.pop('resource_attributes', list())
        for attribute in resource_attributes:
            attribute_item_name = attribute["attribute_definition"].get('name', None)
            try:
                attribute_def = AttributeDefinition.objects.get(name=attribute_item_name)
                try:
                    current_resource_attribute = ResourceAttribute.objects.get(resource=instance, attribute_definition=attribute_def)
                    current_resource_attribute.value = attribute.get('value', current_resource_attribute.value)
                    current_resource_attribute.save()
                except ResourceAttribute.DoesNotExist:
                    # the resource attribute is not yet created
                    ResourceAttribute.objects.create(resource=instance, attribute_definition=attribute_def,
                                                     value=attribute.get('value', 0))

            except AttributeDefinition.DoesNotExist:
                raise serializers.ValidationError({
                    attribute_item_name: f"'{attribute_item_name}' is not a valid attribute of the resource group {instance.resource_group.name}"
                })
        return super(ResourceSerializer, self).update(instance, validated_data)


class ResourceCreateSerializer(serializers.ModelSerializer):

    resource_attributes = ResourceAttributeCreateSerializer(many=True, label="resource_attributes")

    class Meta:
        model = Resource
        fields = ["name", "service_catalog_instance", "is_deleted_on_instance_deletion",
                  "resource_attributes", "resource_group"]

    def validate_resource_attributes(self, attributes):
        resource_group = self.initial_data["resource_group"]
        # check attribute exist
        seen = set()
        for attribute in attributes:
            attribute_name = attribute.get('name')
            # get the attribute
            if not AttributeDefinition.objects.filter(name=attribute_name).exists():
                raise serializers.ValidationError(f"Attribute does not exist '{attribute_name}'")
            attribute_def = AttributeDefinition.objects.get(name=attribute_name)
            # check attribute is linked to the target resource group
            if not Transformer.objects.filter(attribute_definition=attribute_def, resource_group=resource_group).exists():
                raise serializers.ValidationError(f"Attribute '{attribute_name}' not linked to resource group '{resource_group}'")
            # check for duplicate
            if attribute_name not in seen:
                seen.add(attribute_name)
            else:
                raise serializers.ValidationError(f"Duplicate attribute '{attribute_name}'")
        return attributes

    def create(self, validated_data):
        resource_attributes = validated_data.pop('resource_attributes')
        new_resource = super(ResourceCreateSerializer, self).create(validated_data)
        for attribute in resource_attributes:
            attribute_definition = AttributeDefinition.objects.get(name=attribute.get('name'))
            ResourceAttribute.objects.create(value=attribute.pop('value'),
                                             resource=new_resource,
                                             attribute_definition=attribute_definition)
        return new_resource
