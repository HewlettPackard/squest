from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer

from resource_tracker_v2.models import ResourceGroup


class ResourceGroupSerializer(TaggitSerializer, serializers.ModelSerializer):

    tags = TagListSerializerField()

    class Meta:
        model = ResourceGroup
        fields = ["id", "name", "tags"]
