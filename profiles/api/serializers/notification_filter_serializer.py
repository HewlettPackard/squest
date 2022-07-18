from django.forms import SelectMultiple
from rest_framework.fields import MultipleChoiceField
from rest_framework.serializers import ModelSerializer

from profiles.models import NotificationFilter
from service_catalog.models import InstanceState, RequestState


class NotificationFilterSerializer(ModelSerializer):
    request_states = MultipleChoiceField(label="Request states",
                                         required=False,
                                         choices=RequestState.choices
                                         )

    instance_states = MultipleChoiceField(label="Instance states",
                                          required=False,
                                          choices=InstanceState.choices
                                          )

    class Meta:
        model = NotificationFilter
        fields = '__all__'
        read_only_fields = ('id', 'profile')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('context').get('request').user
        super(NotificationFilterSerializer, self).__init__(*args, **kwargs)

    def create(self, validated_data):
        validated_data['profile'] = self.user.profile
        return super(NotificationFilterSerializer, self).create(validated_data)
