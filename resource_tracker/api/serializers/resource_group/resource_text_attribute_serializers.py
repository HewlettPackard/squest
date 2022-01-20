from rest_framework import serializers
from resource_tracker.models import ResourceTextAttribute


class ResourceTextAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceTextAttribute
        fields = ["name", "resource", "value"]
        read_ony_fields = ["resource"]

    name = serializers.CharField(source="text_attribute_type.name")
