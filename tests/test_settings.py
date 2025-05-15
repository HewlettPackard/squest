from django.test import TestCase, override_settings

from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from profiles.models import Token
from service_catalog.apps import create_default_token, create_default_password


class SettingsTest(TestCase):
    # Test admin token creation
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

    # Test admin password creation
    @override_settings(DEFAULT_ADMIN_PASSWORD='Changedp@ssw0rd')
    def test_password_created(self):
        admin_user = User.objects.create_superuser('admin', 'admin@hpe.com', "p@ssw0rd")
        print(admin_user.password)
        check_password(password='Changedp@ssw0rd', encoded=admin_user.password)
        self.assertFalse(check_password(password='Changedp@ssw0rd', encoded=admin_user.password))
        create_default_password()
        admin_user.refresh_from_db()
        self.assertTrue(check_password(password='Changedp@ssw0rd', encoded=admin_user.password))

    def test_password_not_changed_if_not_set(self):
        admin_user = User.objects.create_superuser('admin', 'admin@hpe.com', "p@ssw0rd")
        self.assertFalse(check_password(password='Changedp@ssw0rd', encoded=admin_user.password))
        create_default_password()
        admin_user.refresh_from_db()
        self.assertFalse(check_password(password='Changedp@ssw0rd', encoded=admin_user.password))
