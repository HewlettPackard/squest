from rest_framework import status
from rest_framework.reverse import reverse

from profiles.models import Permission, GlobalPermission, Role
from service_catalog.models import Request, Instance
from tests.test_service_catalog.base_test_request import BaseTestRequestAPI


class TestApiRequestList(BaseTestRequestAPI):

    def setUp(self):
        super(TestApiRequestList, self).setUp()
        self.get_request_list_url = reverse('api_request_list')
        Request.objects.create(
            fill_in_survey={},
            admin_fill_in_survey={'float_var': 1.8},
            instance=self.test_instance,
            operation=self.create_operation_test,
            user=self.standard_user
        )
        Request.objects.create(
            fill_in_survey={},
            admin_fill_in_survey={'float_var': 1.8},
            instance=self.test_instance,
            operation=self.update_operation_test,
            user=self.standard_user
        )
        Request.objects.create(
            fill_in_survey={},
            admin_fill_in_survey={'float_var': 1.8},
            instance=self.test_instance_2,
            operation=self.create_operation_test,
            user=self.standard_user_2
        )
        Request.objects.create(
            fill_in_survey={},
            admin_fill_in_survey={'float_var': 1.8},
            instance=self.test_instance_2,
            operation=self.update_operation_test,
            user=self.standard_user_2
        )

    def test_admin_get_all_requests(self):
        response = self.client.get(self.get_request_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], Request.objects.count())
        self.assertIn('admin_fill_in_survey', response.data['results'][-1].keys())

    def test_cannot_get_request_list_when_logout(self):
        self.client.logout()
        response = self.client.get(self.get_request_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_fill_in_survey_permission_in_request_list_with_superuser(self):
        self.client.force_login(user=self.superuser)
        response = self.client.get(self.get_request_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], Request.objects.count())
        self.assertTrue(response.data['count'] > 0)
        for squest_request in response.data["results"]:
            self.assertIn('admin_fill_in_survey', squest_request.keys())

    def test_admin_fill_in_survey_permission_in_request_list_with_standarduser(self):
        self.client.force_login(user=self.standard_user)
        self.team_member_role.permissions.add(
            Permission.objects.get_by_natural_key(codename="view_request", app_label="service_catalog",
                                                  model="request")
        )
        response = self.client.get(self.get_request_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['count'] > 0)
        self.assertEqual(response.data['count'],
                         Request.get_queryset_for_user(self.standard_user, "service_catalog.view_request").count())
        for squest_request in response.data["results"]:
            self.assertNotIn('admin_fill_in_survey', squest_request.keys())

    def test_admin_fill_in_survey_permission_in_request_list_with_standarduser_with_view_admin_survey_perm(self):
        # Prepare roles and permissions
        self.team_member_role.permissions.add(
            Permission.objects.get_by_natural_key(codename="view_request", app_label="service_catalog",
                                                  model="request")
        )
        globalperm = GlobalPermission.load()
        role_with_perm_admin_survey = Role.objects.create(name="Role with admin survey")
        role_with_perm_admin_survey.permissions.add(
            Permission.objects.get_by_natural_key(codename="view_admin_survey", app_label="service_catalog",
                                                  model="request"))
        globalperm.add_user_in_role(self.standard_user, role_with_perm_admin_survey)


        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.get_request_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['count'] > 0)
        self.assertEqual(response.data['count'],
                         Request.get_queryset_for_user(self.standard_user, "service_catalog.view_request").count())
        for squest_request in response.data["results"]:
            self.assertIn('admin_fill_in_survey', squest_request.keys())
