from rest_framework.fields import MultipleChoiceField
from rest_framework.serializers import ModelSerializer

from profiles.models import RequestNotification
from service_catalog.models import RequestState


class RequestNotificationFilterSerializer(ModelSerializer):
    request_states = MultipleChoiceField(label="Request states",
                                         required=False,
                                         choices=RequestState.choices
                                         )

    class Meta:
        model = RequestNotification
        fields = '__all__'
        read_only_fields = ('id', 'profile')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('context').get('request').user
        super(RequestNotificationFilterSerializer, self).__init__(*args, **kwargs)

    def create(self, validated_data):
        validated_data['profile'] = self.user.profile
        return super(RequestNotificationFilterSerializer, self).create(validated_data)
