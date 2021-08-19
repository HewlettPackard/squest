from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from resource_tracker.models import ResourceGroup, Resource, ResourceAttribute, ResourceTextAttribute, \
    ResourceGroupAttributeDefinition, ResourceGroupTextAttributeDefinition
from service_catalog.models import Instance


class ResourceGroupAttributeDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceGroupAttributeDefinition
        fields = ["id", "name"]


class ResourceGroupTextAttributeDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceGroupTextAttributeDefinition
        fields = ["id", "name"]


class ResourceAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceAttribute
        fields = ["name", "value"]

    name = serializers.SerializerMethodField(method_name="get_attribute_name")

    @staticmethod
    def get_attribute_name(resource_attribute):
        return resource_attribute.attribute_type.name


class ResourceTextAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceTextAttribute
        fields = ["name", "value"]

    name = serializers.SerializerMethodField(method_name="get_text_attribute_name")

    @staticmethod
    def get_text_attribute_name(resource_attribute):
        return resource_attribute.text_attribute_type.name


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ["id", "name", "service_catalog_instance", "attributes", "text_attributes"]

    attributes = ResourceAttributeSerializer(many=True)
    text_attributes = ResourceTextAttributeSerializer(many=True)


class ResourceGroupSerializer(serializers.ModelSerializer):
    resources = ResourceSerializer(many=True, read_only=True)

    class Meta:
        model = ResourceGroup
        fields = '__all__'


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
