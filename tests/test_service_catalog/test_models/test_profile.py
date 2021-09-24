from django.contrib.auth.models import User

from profiles.models import Profile
from tests.test_service_catalog.base import BaseTest


class TestProfile(BaseTest):

    def setUp(self):
        super(TestProfile, self).setUp()

    def test_one_to_one_user_on_create(self):
        users_count = User.objects.all().count()
        profile_count = Profile.objects.all().count()
        self.assertEquals(users_count, profile_count)
        User.objects.create(username='test_profile_user')
        users_count = User.objects.all().count()
        profile_count = Profile.objects.all().count()
        self.assertEquals(users_count, profile_count)
