from rest_framework import serializers
from resource_tracker.models import ResourceAttribute


class ResourceAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceAttribute
        fields = ["name", "resource", "value"]
        read_ony_fields = ["resource"]

    name = serializers.CharField(source="attribute_type.name")
