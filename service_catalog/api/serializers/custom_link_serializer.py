from rest_framework.serializers import ModelSerializer

from service_catalog.models import CustomLink


class CustomLinkSerializer(ModelSerializer):
    class Meta:
        model = CustomLink
        fields = ('id', 'name', 'services', 'text', 'url', 'button_class', 'when', 'loop', 'enabled', 'is_admin_only')
        read_only_fields = ('id',)
