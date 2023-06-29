from django.contrib.contenttypes.models import ContentType
from rest_framework.serializers import ModelSerializer


class ContentTypeSerializer(ModelSerializer):
    class Meta:
        model = ContentType
        fields = '__all__'
