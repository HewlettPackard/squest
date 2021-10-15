from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from resource_tracker.api.serializers.resource_group.attribute_definition_serializers import AttributeCreateSerializer
from resource_tracker.api.serializers.resource_group.text_attribute_definition_serializers import \
    TextAttributeCreateSerializer
from resource_tracker.models import Resource, ResourceAttribute, ResourceTextAttribute, \
    ResourceGroupAttributeDefinition, ResourceGroupTextAttributeDefinition
from service_catalog.models import Instance


class ResourceAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceAttribute
        fields = ["name", "resource", "value"]
        read_ony_fields = ["resource"]

    name = serializers.CharField(source="attribute_type.name")


class ResourceTextAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceTextAttribute
        fields = ["name", "resource", "value"]
        read_ony_fields = ["resource"]

    name = serializers.CharField(source="text_attribute_type.name")


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ["id", "resource_group", "name", "service_catalog_instance", "attributes", "text_attributes"]
        read_ony_fields = ["resource_group"]

    attributes = ResourceAttributeSerializer(many=True)
    text_attributes = ResourceTextAttributeSerializer(many=True)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.service_catalog_instance = validated_data.get('service_catalog_instance',
                                                               instance.service_catalog_instance)
        instance.save()

        attributes = validated_data.get('attributes')
        for attribute in attributes:
            attribute_item_name = attribute["attribute_type"].get('name', None)
            try:
                attribute_def = ResourceGroupAttributeDefinition.objects.get(resource_group_definition=instance.resource_group,
                                                                             name=attribute_item_name)
                attribute_item = ResourceAttribute.objects.get(resource=instance, attribute_type=attribute_def)
                attribute_item.value = attribute.get('value', attribute_item.value)
                attribute_item.save()
            except ResourceGroupAttributeDefinition.DoesNotExist:
                raise serializers.ValidationError({
                    attribute_item_name: f'Not a valid attribute of the resource group {instance.resource_group.name}'
                })

        text_attributes = validated_data.get('text_attributes')
        for text_attribute in text_attributes:
            text_attribute_item_name = text_attribute["text_attribute_type"].get('name', None)
            try:
                text_attribute_def = ResourceGroupTextAttributeDefinition.objects.get(resource_group_definition=instance.resource_group,
                                                                                      name=text_attribute_item_name)
                text_attribute_item = ResourceTextAttribute.objects.get(resource=instance,
                                                                        text_attribute_type=text_attribute_def)
                text_attribute_item.value = text_attribute.get('value', text_attribute_item.value)
                text_attribute_item.save()
            except ResourceGroupTextAttributeDefinition.DoesNotExist:
                raise serializers.ValidationError({
                    text_attribute_item_name: f'Not a valid text attribute of the resource group '
                                              f'{instance.resource_group.name}'
                })
        return instance


class ResourceCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    attributes = AttributeCreateSerializer(many=True)
    text_attributes = TextAttributeCreateSerializer(many=True)
    service_catalog_instance = PrimaryKeyRelatedField(queryset=Instance.objects.all(),
                                                      allow_null=True)

    def validate_attributes(self, attributes):
        seen = set()
        for attribute in attributes:
            t = tuple(attribute.items())
            if t[0][1] not in seen:
                seen.add(t[0][1])
            else:
                raise serializers.ValidationError(f"Duplicate attribute '{t[0][1]}'")
        return attributes

    def validate_text_attributes(self, text_attributes):
        seen = set()
        for text_attribute in text_attributes:
            t = tuple(text_attribute.items())
            if t[0][1] not in seen:
                seen.add(t[0][1])
            else:
                raise serializers.ValidationError(f"Duplicate text attribute '{t[0][1]}'")
        return text_attributes

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
        new_resource = Resource.objects.create(name=validated_data['name'], resource_group=resource_group)
        if validated_data['service_catalog_instance'] is not None:
            new_resource.service_catalog_instance = validated_data['service_catalog_instance']
            new_resource.save()
        attributes = validated_data.pop('attributes')
        for attribute in attributes:
            attribute_type = ResourceGroupAttributeDefinition.objects.get(name=attribute.pop('name'),
                                                                          resource_group_definition=resource_group)
            ResourceAttribute.objects.create(value=attribute.pop('value'),
                                             resource=new_resource,
                                             attribute_type=attribute_type)
        text_attributes = validated_data.pop('text_attributes')
        for text_attribute in text_attributes:
            text_attribute_type = ResourceGroupTextAttributeDefinition.objects.get(name=text_attribute.pop('name'),
                                                                                   resource_group_definition=resource_group)
            ResourceTextAttribute.objects.create(value=text_attribute.pop('value'),
                                                 resource=new_resource,
                                                 text_attribute_type=text_attribute_type)
        return new_resource
