from django.urls import reverse
from django.utils import timezone

from profiles.models import Token
from tests.test_group.test_group_base import TestGroupBase


class TestProfileUrls(TestGroupBase):

    def setUp(self):
        super(TestProfileUrls, self).setUp()
        self.token = Token.objects.create(user=self.superuser)
        self.args_token = {
            'token_id': self.token.id
        }

    def test_all_get(self):
        urls_list = [
            reverse('profiles:profile'),
            reverse('profiles:token_edit', kwargs=self.args_token),
            reverse('profiles:user_list')
        ]
        for url in urls_list:
            response = self.client.get(url)
            self.assertEquals(200, response.status_code)

    def test_all_get_redirect(self):
        urls_list = [
            reverse('profiles:token_generate', kwargs=self.args_token),
        ]
        for url in urls_list:
            response = self.client.get(url)
            self.assertEquals(302, response.status_code)

    def test_all_post_with_data(self):
        test_list = [
            {'url': reverse('profiles:token_edit', kwargs=self.args_token),
             'data': {'key': self.token.generate_key(), 'expires': timezone.now() + timezone.timedelta(days=2)}},
        ]
        for test in test_list:
            response = self.client.post(test['url'], data=test['data'])
            self.assertEquals(302, response.status_code)
