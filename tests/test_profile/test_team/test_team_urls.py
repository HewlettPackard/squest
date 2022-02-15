from django.urls import reverse

from profiles.models import TeamRoleBinding, Team, Role
from service_catalog.models import Instance
from tests.test_profile.test_group.test_group_base import TestGroupBase


class TestTeamUrls(TestGroupBase):

    def setUp(self):
        super(TestTeamUrls, self).setUp()
        instance = Instance.objects.create(name="test")
        instance.add_team_in_role(self.test_team, "Admin")
        self.client.force_login(self.my_user2)
        self.args_user = {
            'user_id': self.my_user.id
        }
        self.args_team = {
            'team_id': self.test_team.id
        }
        self.args_role_binding = {
            'team_role_binding_id': TeamRoleBinding.objects.filter(team=self.test_team).first().id
        }

    def test_all_get(self):
        urls_list = [
            reverse('profiles:team_create'),
            reverse('profiles:team_list'),
            reverse('profiles:team_details', kwargs=self.args_team),
            reverse('profiles:team_role_binding_create', kwargs=self.args_team),
            reverse('profiles:team_role_binding_delete', kwargs={**self.args_team, **self.args_role_binding}),
            reverse('profiles:user_in_team_update', kwargs=self.args_team),
            reverse('profiles:team_edit', kwargs=self.args_team),
            reverse('profiles:team_delete', kwargs=self.args_team),
            reverse('profiles:user_in_team_remove', kwargs={**self.args_team, **self.args_user}),
        ]
        for url in urls_list:
            response = self.client.get(url)
            self.assertEqual(200, response.status_code)
        self.client.logout()
        for url in urls_list:
            print(url)
            response = self.client.get(url)
            self.assertEqual(302, response.status_code)
        self.client.force_login(self.standard_user)
        urls_list.remove(reverse('profiles:team_create'))
        urls_list.remove(reverse('profiles:team_list'))
        for url in urls_list:
            response = self.client.get(url)
            self.assertEqual(403, response.status_code)

    def test_remove_user_in_team(self):
        url = reverse('profiles:user_in_team_remove', kwargs={**self.args_team, **self.args_user})
        response = self.client.post(url)
        self.assertEqual(302, response.status_code)
        self.test_team.refresh_from_db()
        self.assertNotIn(self.my_user, self.test_team.get_all_users())

    def test_delete_team_role_bindings(self):
        url = reverse('profiles:team_role_binding_delete', kwargs={**self.args_team, **self.args_role_binding})
        response = self.client.post(url)
        self.assertEqual(302, response.status_code)
        self.assertFalse(TeamRoleBinding.objects.filter(id=self.args_role_binding['team_role_binding_id']).exists())

    def test_delete_team(self):
        url = reverse('profiles:team_delete', kwargs=self.args_team)
        response = self.client.post(url)
        self.assertEqual(302, response.status_code)
        self.assertFalse(Team.objects.filter(id=self.args_team['team_id']).exists())

    def test_create_team(self):
        old_count = Team.objects.count()
        url = reverse('profiles:team_create')
        data = {'name': 'team_test2'}
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(old_count + 1, Team.objects.count())
        self.assertEqual(Team.objects.last().name, data['name'])

    def test_edit_team(self):
        url = reverse('profiles:team_edit', kwargs=self.args_team)
        data = {'name': 'team_test_renamed'}
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(Team.objects.get(id=self.args_team['team_id']).name,'team_test_renamed')

    def test_update_user_in_team(self):
        role = self.test_team.roles.first()
        old_count = self.test_team.get_users_in_role(role.name).count()
        url = reverse('profiles:user_in_team_update', kwargs=self.args_team)
        data = {'users': [self.my_user2.id], 'roles': str(role.id)}
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(len(data['users']), self.test_team.get_users_in_role(role.name).count())
        self.assertNotEqual(old_count, self.test_team.get_users_in_role(role.name).count())
