from django.urls import reverse
from django.utils import timezone

from profiles.forms.token_forms import TokenForm
from profiles.models import Token
from tests.test_profile.test_group.test_group_base import TestGroupBase


class TestToken(TestGroupBase):

    def setUp(self):
        super(TestToken, self).setUp()
        self.token = Token.objects.create(user=self.superuser, description='Initial')
        self.args_token = {
            'token_id': self.token.id
        }

    def test_all_get(self):
        urls_list = [
            reverse('profiles:token_create'),
            reverse('profiles:token_edit', kwargs=self.args_token),
            reverse('profiles:token_delete', kwargs=self.args_token),
        ]
        for url in urls_list:
            response = self.client.get(url)
            self.assertEqual(200, response.status_code)
        self.client.logout()
        for url in urls_list:
            response = self.client.get(url)
            self.assertEqual(302, response.status_code)

    def test_all_get_redirect(self):
        original_key = self.token.key
        response = self.client.get(reverse('profiles:token_generate', kwargs=self.args_token))
        self.assertEqual(302, response.status_code)
        self.token.refresh_from_db()
        self.assertNotEqual(original_key, self.token.key)

    def test_all_post_with_data(self):
        test = [
            {'url': reverse('profiles:token_create'),
             'data': {'description': 'My description', 'expires': timezone.now() + timezone.timedelta(days=2)}},
            {'url': reverse('profiles:token_edit', kwargs=self.args_token),
             'data': {'description': 'Edited description', 'expires': timezone.now() + timezone.timedelta(days=4)}},
            {'url': reverse('profiles:token_delete', kwargs=self.args_token),
             'data': {}}
        ]
        initial = Token.objects.filter(description='Initial').count()
        initial_created = Token.objects.filter(description='My description').count()
        initial_edited = Token.objects.filter(description='Edited description').count()
        response = self.client.post(test[0]['url'], data=test[0]['data'])
        self.assertEqual(302, response.status_code)
        self.assertTrue(Token.objects.filter(description='My description').count() == initial_created + 1)
        response = self.client.post(test[1]['url'], data=test[1]['data'])
        self.assertEqual(302, response.status_code)
        self.assertTrue(Token.objects.filter(description='Initial').count() == initial - 1)
        self.assertTrue(Token.objects.filter(description='Edited description').count() == initial_edited + 1)
        response = self.client.post(test[2]['url'], data=test[2]['data'])
        self.assertEqual(302, response.status_code)
        self.assertTrue(Token.objects.filter(description='Edited description').count() == initial_edited)

    def test_create_token_with_expired_date(self):
        data = {'expires': timezone.now() - timezone.timedelta(days=2),
                'description': ''}
        form = TokenForm(data)
        self.assertFalse(form.is_valid())
