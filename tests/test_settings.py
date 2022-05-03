from django.test import TestCase, override_settings

from django.contrib.auth.models import User

from profiles.models import Token
from service_catalog.apps import create_default_token


class SettingsTest(TestCase):

    @override_settings(DEFAULT_ADMIN_TOKEN='xxxxx')
    def test_token_created(self):
        User.objects.create_superuser('admin', 'admin@hpe.com', "p@ssw0rd")
        self.assertEqual(Token.objects.count(), 0)
        create_default_token()
        self.assertTrue(Token.objects.filter(key="xxxxx").exists())
        self.assertEqual(Token.objects.count(), 1)

    def test_token_not_created_if_not_set(self):
        User.objects.create_superuser('admin', 'admin@hpe.com', "p@ssw0rd")
        self.assertEqual(Token.objects.count(), 0)
        create_default_token()
        self.assertEqual(Token.objects.count(), 0)
