from django.urls import reverse

from profiles.models import UserRoleBinding
from tests.test_profile.test_group.test_group_base import TestGroupBase


class TestTeamUrls(TestGroupBase):

    def setUp(self):
        super(TestTeamUrls, self).setUp()
        self.client.force_login(self.my_user2)

    def test_all_get(self):
        args_user = {
            'user_id': self.my_user.id
        }
        args_team = {
            'team_id': self.test_team.id
        }
        urls_list = [
            reverse('profiles:team_create'),
            reverse('profiles:team_list'),
            reverse('profiles:team_details', kwargs=args_team),
            reverse('profiles:user_in_team_update', kwargs=args_team),
            reverse('profiles:team_edit', kwargs=args_team),
            reverse('profiles:team_delete', kwargs=args_team),
            reverse('profiles:user_in_team_remove', kwargs={**args_team, **args_user}),
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

    def test_all_delete_post(self):
        args_user = {
            'user_id': self.my_user.id
        }
        args_team = {
            'team_id': self.test_team.id
        }
        urls_list = [
            reverse('profiles:user_in_team_remove', kwargs={**args_team, **args_user}),
            reverse('profiles:team_delete', kwargs=args_team)
        ]
        for url in urls_list:
            response = self.client.post(url)
            self.assertEqual(302, response.status_code)

    def test_all_post_with_data(self):
        args_team = {
            'team_id': self.test_team.id
        }
        test_list = [
            {'url': reverse('profiles:team_create'), 'data': {'name': 'team_test2'}},
            {'url': reverse('profiles:team_edit', kwargs=args_team),
             'data': {'name': 'team_test_renamed'}},
            {'url': reverse('profiles:user_in_team_update', kwargs=args_team),
             'data': {'users': [self.my_user2.id, self.my_user3.id], 'roles': str(self.test_team.roles.first().id)}}
        ]
        for test in test_list:
            response = self.client.post(test['url'], data=test['data'])
            self.assertEqual(302, response.status_code)
