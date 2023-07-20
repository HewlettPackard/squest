from rest_framework.serializers import ModelSerializer, Serializer, CharField

from service_catalog.models import RequestMessage


class MessageSerializer(Serializer):
    content = CharField(
        label="Message",
        help_text="Message attached to this request"
    )


class RequestMessageReadSerializer(ModelSerializer):
    class Meta:
        model = RequestMessage
        fields = '__all__'


class RequestMessageSerializer(ModelSerializer):
    class Meta:
        model = RequestMessage
        fields = ('sender', 'request', 'content')
