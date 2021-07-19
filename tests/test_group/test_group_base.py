from django.contrib.auth.models import Group, User

from tests.base import BaseTest


class TestGroupBase(BaseTest):

    def setUp(self):
        super(TestGroupBase, self).setUp()
        self.my_group = Group.objects.create(name='test_group')
        self.my_user = User.objects.create(username='test_user')
        self.my_user2 = User.objects.create(username='test_user2')
        self.my_user3 = User.objects.create(username='test_user3')
        self.my_user4 = User.objects.create(username='test_user4')
        self.my_group.user_set.add(self.my_user)
        self.my_group.user_set.add(self.my_user3)
