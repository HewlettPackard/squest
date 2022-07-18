from tests.test_service_catalog.base import BaseTest
from profiles.api.serializers.user_serializers import UserSerializer


class TestUserSerializer(BaseTest):

    def setUp(self):
        super(TestUserSerializer, self).setUp()
        self.superuser.profile.notification_enabled = True
        self.superuser.profile.save()

    def test_contains_expected_fields(self):
        serializer = UserSerializer(instance=self.superuser)
        self.assertEqual(set(serializer.data.keys()),
                         {'id', 'last_name', 'first_name', 'is_staff', 'email',
                          'profile', 'username', 'is_superuser', 'is_active'})

    def test_user_field_content(self):
        serializer = UserSerializer(instance=self.superuser)
        self.assertEqual(serializer.data['id'], self.superuser.id)
        self.assertEqual(serializer.data['email'], self.superuser.email)
        self.assertEqual(serializer.data['username'], self.superuser.username)
        self.assertEqual(serializer.data['profile']['notification_enabled'], True)
        self.assertEqual(serializer.data['profile']['notification_filters'], [])
