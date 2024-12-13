from django.test import TestCase
from rest_framework.test import APIClient

from django.contrib.auth.models import User
from profiles.models.squest_permission import Permission
from django.urls import reverse, NoReverseMatch

from profiles.models import GlobalScope, Role


class TestingContextView:
    expected_status_code = None
    expected_not_allowed_status_code = None

    def __init__(self, url, perm_str_list, url_kwargs=None, data=None, expected_status_code=None,
                 expected_not_allowed_status_code=None, follow=None):
        if expected_not_allowed_status_code is not None:
            self.expected_not_allowed_status_code = expected_not_allowed_status_code
        if expected_status_code is not None:
            self.expected_status_code = expected_status_code

        self.follow = follow or False
        try:
            self.url = reverse(url, kwargs=url_kwargs)
        except NoReverseMatch:
            raise NoReverseMatch(f'url: {url}, kwargs: {url_kwargs}')
        self.data = {} if data is None else data

        permission_id = list()
        for perm_str in perm_str_list:
            try:
                permission_id.append(Permission.objects.get(content_type__app_label=perm_str.split('.')[0],
                                                         codename=perm_str.split('.')[1]).id)
            except Permission.DoesNotExist:
                raise Permission.DoesNotExist(f'Permission {perm_str_list} does not exist.')
            except Permission.MultipleObjectsReturned:
                raise Permission.MultipleObjectsReturned(
                    Permission.objects.filter(content_type__app_label=perm_str.split('.')[0],
                                              codename=perm_str.split('.')[1]))
        self.permissions = Permission.objects.filter(id__in=permission_id)

    def __str__(self):
        return f"{str(self.__class__)} - {self.url} - {self.permissions}"

    def call_url(self, client):
        raise NotImplemented

    def get_expected_status_code(self, client):
        if self.expected_status_code is not None:
            return self.expected_status_code
        raise NotImplemented

    def get_expected_not_allowed_status_code(self, client):
        if self.expected_not_allowed_status_code is not None:
            return self.expected_not_allowed_status_code
        return 403


class TestingGetContextView(TestingContextView):
    expected_status_code = 200

    def call_url(self, client):
        return client.get(self.url, self.data, follow=self.follow)


class TestingPostContextView(TestingContextView):
    def call_url(self, client):
        if isinstance(client, APIClient):
            return client.post(self.url, self.data, format="json")
        return client.post(self.url, self.data, follow=self.follow)

    def get_expected_status_code(self, client):
        if self.expected_status_code is not None:
            return self.expected_status_code
        elif isinstance(client, APIClient):
            return 201
        return 302


class TestingPutContextView(TestingContextView):
    expected_status_code = 200

    def call_url(self, client):
        return client.put(self.url, self.data, format="json", follow=self.follow)


class TestingPatchContextView(TestingContextView):
    expected_status_code = 200

    def call_url(self, client):
        return client.patch(self.url, self.data, format="json", follow=self.follow)


class TestingDeleteContextView(TestingContextView):
    expected_status_code = 204

    def call_url(self, client):
        return client.delete(self.url, self.data, format="json", follow=self.follow)


class TestPermissionEndpoint(TestCase):
    def setUp(self):
        super().setUp()
        self.global_scope = GlobalScope.load()
        self.global_scope.global_permissions.clear()
        self.testing_user = User.objects.create_user('testing_view_user', 'testing_view_user@hpe.com', "password")
        self.empty_role = Role.objects.create(name='empty', description='empty for testing')
        self.global_scope.add_user_in_role(self.testing_user, self.empty_role)
        self.client.force_login(self.testing_user)

    def run_permissions_tests(self, testing_list):
        for test_context in testing_list:
            test_context: TestingContextView = test_context
            response = test_context.call_url(self.client)
            self.assertEqual(test_context.get_expected_not_allowed_status_code(self.client), response.status_code,
                             f"{test_context}: expected: {test_context.get_expected_not_allowed_status_code(self.client)}, got: {response.status_code}")
            # for permission in test_context.permissions:
            self.empty_role.permissions.add(*test_context.permissions)
            response = test_context.call_url(self.client)
            if response.status_code == 400:
                print(response.content)
            self.assertEqual(test_context.get_expected_status_code(self.client), response.status_code,
                             f"{test_context}: expected: {test_context.get_expected_status_code(self.client)}, got: {response.status_code}")
            for permission in test_context.permissions:
                self.empty_role.permissions.remove(permission)