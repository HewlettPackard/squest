from django.contrib.auth.models import Group, User

from profiles.models.team import Team
from tests.test_service_catalog.base import BaseTest


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
        self.test_team = Team.objects.create(name='test_team')
        self.test_team.add_user_in_role(self.my_user2, "Admin")
        self.test_team.add_user_in_role(self.my_user3, "Admin")
        self.test_team.add_user_in_role(self.my_user2, "Member")
        self.test_team2 = Team.objects.create(name='test_team2')
        self.test_team2.add_user_in_role(self.my_user, "Admin")
        self.test_team.add_user_in_role(self.my_user4, "Member")
        self.test_billing_group.user_set.add(self.my_user2)
