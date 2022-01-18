from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from tests.test_profile.test_group.test_group_base import TestGroupBase


class TestAjax(TestGroupBase):

    def setUp(self):
        super(TestAjax, self).setUp()
        self.data = {
            'role_id': self.test_team.roles.first().id,
            'content_type_id': ContentType.objects.get_for_model(self.test_team).id,
            'object_id': self.test_team.id,
        }
        self.url_user = reverse("profiles:get_users_with_role")
        self.url_team = reverse("profiles:get_teams_with_role")

    def test_can_get_users_and_teams(self):
        self.client.force_login(self.my_user2)
        response = self.client.get(self.url_user, data=self.data)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.url_team, data=self.data)
        self.assertEqual(response.status_code, 200)

    def test_permission_refused_for_non_member(self):
        self.client.force_login(self.standard_user)
        response = self.client.get(self.url_user, data=self.data)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_team, data=self.data)
        self.assertEqual(response.status_code, 403)

    def test_permission_refused_when_logout(self):
        self.client.logout()
        response = self.client.get(self.url_user, data=self.data)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(self.url_team, data=self.data)
        self.assertEqual(response.status_code, 302)



