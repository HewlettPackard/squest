from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from profiles.models import Team, UserRoleBinding
from tests.test_profile.test_group.test_group_base import TestGroupBase


class TestTeamModel(TestGroupBase):

    def setUp(self):
        super(TestTeamModel, self).setUp()

    def test_create_team(self):
        self.client.force_login(self.standard_user)
        url = reverse('profiles:team_create')
        test_list = [
            {'data': {'name': 'new_team'}, 'created': True},
            {'data': {'name': 'test_team2'}, 'created': False},
            {'data': {'name': ''}, 'created': False},
            {'data': {'foo': 'group'}, 'created': False},
        ]
        team_count = len(Team.objects.all())
        for test in test_list:
            self.client.post(url, data=test['data'])
            if test['created']:
                team_count += 1
                team = Team.objects.get(name=test['data']['name'])
                self.assertIn(self.standard_user, team.get_all_users())
                self.assertIn(self.standard_user, team.get_users_in_role("Admin"))
            self.assertEqual(len(Team.objects.all()), team_count)

    def test_admin(self):
        self.client.force_login(self.superuser)
        self._assert_edit()
        self._assert_update_team_member()
        self._assert_delete()

    def test_team_admin(self):
        self.client.force_login(self.test_team.get_users_in_role("Admin").first())
        self._assert_edit()
        self._assert_update_team_member()
        self._assert_delete()

    def test_team_member(self):
        self.client.force_login(
            self.test_team.get_users_in_role("Member").exclude(
                id__in=[user.id for user in self.test_team.get_users_in_role("Admin")]).first())
        self._assert_edit(False)
        self._assert_update_team_member(False)
        self._assert_delete(False)

    def test_not_team_member(self):
        if self.standard_user_2 not in self.test_team.get_all_users():
            self.client.force_login(self.standard_user_2)
            self._assert_edit(False)
            self._assert_update_team_member(False)
            self._assert_delete(False)

    def test_team_admin_of_other_team(self):
        if self.my_user in self.test_team2.get_users_in_role("Admin"):
            self.client.force_login(self.my_user)
            self._assert_edit(False)
            self._assert_update_team_member(False)
            self._assert_delete(False)

    def _assert_edit(self, authorized=True):
        args_group = {
            'team_id': self.test_team.id
        }
        old_name = self.test_team.name
        new_name = 'new_name'
        url = reverse('profiles:team_edit', kwargs=args_group)
        data = {'name': new_name}
        self.client.post(url, data=data)
        self.assertEqual(Team.objects.get(id=self.test_team.id).name, new_name if authorized else old_name)

    def _assert_delete(self, authorized=True):
        args_group = {
            'team_id': self.test_team.id
        }
        url = reverse('profiles:team_delete', kwargs=args_group)
        self.assertTrue(Team.objects.filter(id=self.test_team.id).exists())
        for i in range(2):
            self.client.post(url)
            if authorized:
                self.assertFalse(Team.objects.filter(id=self.test_team.id).exists())
            else:
                self.assertTrue(Team.objects.filter(id=self.test_team.id).exists())

    def _assert_update_team_member(self, authorized=True):
        args_group = {
            'team_id': self.test_team.id
        }
        logged_user = User.objects.get(id=self.client.session['_auth_user_id'])
        url = reverse('profiles:user_in_team_update', kwargs=args_group)
        roles = self.test_team.roles
        data_list = [
            {'users': [self.my_user.id, self.my_user2.id, self.my_user3.id, self.my_user4.id]},
            {'users': [self.my_user.id]},
            {'users': [self.my_user2.id, self.my_user3.id]},
        ]
        for role in roles:
            old_users = self.test_team.get_users_in_role(role.name)
            for data in data_list:
                data['roles'] = str(role.id)
                if logged_user.id not in data['users'] and role.name == "Admin":
                    data['users'].append(logged_user.id)
                response = self.client.post(url, data=data)
                self.test_team.refresh_from_db()
                if authorized:
                    self.assertEqual(list(set(data.get('users', []))),
                                     list(set([user.id for user in self.test_team.get_users_in_role(role.name)])))
                else:
                    self.assertEqual(list(set([user.id for user in old_users])),
                                     list(set([user.id for user in self.test_team.get_users_in_role(role.name)])))

    def test_remove_team_member(self):
        test_list = [
            {'args_user': {'user_id': self.my_user.id}, 'offset': 0},
            {'args_user': {'user_id': self.my_user2.id}, 'offset': 1},
            {'args_user': {'user_id': self.my_user4.id}, 'offset': 2},
            {'args_user': {'user_id': self.my_user3.id}, 'offset': 2}
        ]
        args_group = {
            'team_id': self.test_team.id
        }
        init_users_len = len(self.test_team.get_all_users())
        for test_data in test_list:
            url = reverse('profiles:user_in_team_remove',
                          kwargs={**args_group, **test_data['args_user']})
            response = self.client.post(url)
            self.assertEqual(len(self.test_team.get_all_users()), init_users_len - test_data['offset'])

    def test_remove_permission(self):
        admin_role = self.test_team.roles.get(name="Admin")
        member_role = self.test_team.roles.get(name="Member")
        UserRoleBinding.objects.get(user=self.my_user2, content_type=ContentType.objects.get_for_model(Team),
                                    object_id=self.test_team.id, role=admin_role).delete()
        UserRoleBinding.objects.get(user=self.my_user2, content_type=ContentType.objects.get_for_model(Team),
                                    object_id=self.test_team.id, role=member_role).delete()
        for permission in admin_role.permissions.all():
            self.assertFalse(self.my_user2.has_perm(permission.codename, self.test_team))
        for permission in member_role.permissions.all():
            self.assertFalse(self.my_user2.has_perm(permission.codename, self.test_team))

    def test_not_remove_permission_if_in_other_role(self):
        admin_role = self.test_team.roles.get(name="Admin")
        member_role = self.test_team.roles.get(name="Member")
        UserRoleBinding.objects.get(user=self.my_user2, content_type=ContentType.objects.get_for_model(Team),
                                    object_id=self.test_team.id, role=admin_role).delete()
        for permission in admin_role.permissions.all():
            if permission not in member_role.permissions.all():
                self.assertFalse(self.my_user2.has_perm(permission.codename, self.test_team))
        for permission in member_role.permissions.all():
            self.assertTrue(self.my_user2.has_perm(permission.codename, self.test_team))
