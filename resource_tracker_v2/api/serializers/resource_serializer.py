from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from resource_tracker_v2.models import Resource, ResourceAttribute, AttributeDefinition, Transformer
from service_catalog.models import Instance


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
        read_ony_fields = ["resource_group"]

    resource_attributes = ResourceAttributeSerializer(many=True)


class ResourceCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    resource_attributes = ResourceAttributeCreateSerializer(many=True)
    service_catalog_instance = PrimaryKeyRelatedField(queryset=Instance.objects.all(), allow_null=True)
    is_deleted_on_instance_deletion = serializers.BooleanField(default=True)

    def validate_attributes(self, attributes):
        seen = set()
        for attribute in attributes:
            t = tuple(attribute.items())
            if t[0][1] not in seen:
                seen.add(t[0][1])
            else:
                raise serializers.ValidationError(f"Duplicate attribute '{t[0][1]}'")
        return attributes

    def validate_name(self, value):
        resource_group = self.context.get('resource_group')
        try:
            Resource.objects.get(name=value, resource_group=resource_group)
            raise serializers.ValidationError(f"Resource with this name exist already in resource "
                                              f"group {resource_group.name}")
        except Resource.DoesNotExist:
            return value

    def create(self, validated_data):
        resource_group = self.context.get('resource_group')
        # create the resource
        new_resource = Resource.objects.create(
            name=validated_data['name'],
            resource_group=resource_group,
            is_deleted_on_instance_deletion=validated_data['is_deleted_on_instance_deletion']
        )
        if validated_data['service_catalog_instance'] is not None:
            new_resource.service_catalog_instance = validated_data['service_catalog_instance']
            new_resource.save()
        resource_attributes = validated_data.pop('resource_attributes')
        for attribute in resource_attributes:
            attribute_definition = AttributeDefinition.objects.get(name=attribute.pop('name'))
            ResourceAttribute.objects.create(value=attribute.pop('value'),
                                             resource=new_resource,
                                             attribute_definition=attribute_definition)
        return new_resource
