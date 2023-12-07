from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer, CharField

from profiles.models import Profile


class ProfileSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = ['request_notification_enabled', 'instance_notification_enabled',
                  'request_notification_filters', 'instance_notification_filters']


class UserSerializerNested(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser',
                  'is_active']
        read_only_fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff',
                            'is_superuser', 'is_active']


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'profile', 'first_name', 'last_name', 'is_staff',
                  'is_superuser', 'is_active', 'groups']
        read_only_fields = ['groups', ]

    profile = ProfileSerializer(required=False)
    password = CharField(
        write_only=True,
        required=True,
        help_text='Leave empty if no change needed',
        style={'input_type': 'password', 'placeholder': 'Password'}
    )

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        return super(UserSerializer, self).create(validated_data)
