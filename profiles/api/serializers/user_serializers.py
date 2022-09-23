from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework import serializers

from profiles.models import Profile


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['notification_enabled', 'notification_filters']


class UserSerializer(serializers.ModelSerializer):

    profile = ProfileSerializer(required=False)
    password = serializers.CharField(
        write_only=True,
        required=True,
        help_text='Leave empty if no change needed',
        style={'input_type': 'password', 'placeholder': 'Password'}
    )

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        return super(UserSerializer, self).create(validated_data)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'profile', 'first_name', 'last_name', 'is_staff',
                  'is_superuser', 'is_active', 'billing_groups']
        read_only_fields = ['billing_groups']
