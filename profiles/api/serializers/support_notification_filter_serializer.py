from rest_framework.fields import MultipleChoiceField
from rest_framework.serializers import ModelSerializer

from profiles.models import InstanceNotification
from service_catalog.models import InstanceState


class InstanceNotificationFilterSerializer(ModelSerializer):
    instance_states = MultipleChoiceField(label="Instance states",
                                          required=False,
                                          choices=InstanceState.choices
                                          )

    class Meta:
        model = InstanceNotification
        fields = '__all__'
        read_only_fields = ['profile', ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('context').get('request').user
        super(InstanceNotificationFilterSerializer, self).__init__(*args, **kwargs)

    def create(self, validated_data):
        validated_data['profile'] = self.user.profile
        return super(InstanceNotificationFilterSerializer, self).create(validated_data)
