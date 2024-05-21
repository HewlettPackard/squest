import json
from copy import copy

from django.urls import reverse

from profiles.models import Permission
from service_catalog.models import Support, Instance, Request, InstanceState
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestAdminInstanceViews(BaseTestRequest):

    def setUp(self):
        super(TestAdminInstanceViews, self).setUp()
        self.args = {
            "pk": self.test_instance.id
        }
        self.json_spec = {
            "key1": "val1",
            "key2": "val2"
        }
        self.edit_instance_data = {
            "name": "new_instance_name",
            "service": self.service_test_2.id,
            "requester": self.standard_user_2.id,
            "state": InstanceState.PROVISIONING,
            "quota_scope": self.test_quota_scope.id,
            "spec": json.dumps(self.json_spec),
            "user_spec": json.dumps(self.json_spec),
        }

    def test_get_instance_list(self):
        url = reverse('service_catalog:instance_list')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["table"].data.data), 2)

    def test_cannot_get_instance_list_when_logout(self):
        self.client.logout()
        url = reverse('service_catalog:instance_list')
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)

    def test_admin_can_get_details(self):
        self.test_instance.requester = None
        self.test_instance.save()
        url = reverse('service_catalog:instance_details', kwargs=self.args)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_cannot_get_instance_details_when_logout(self):
        self.client.logout()
        url = reverse('service_catalog:instance_details', kwargs=self.args)
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)

    def test_customer_cannot_get_details_on_non_own_instance(self):
        self.client.login(username=self.standard_user_2, password=self.common_password)
        url = reverse('service_catalog:instance_details', kwargs=self.args)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

    def test_instance_edit(self):
        url = reverse('service_catalog:instance_edit', kwargs=self.args)

        response = self.client.post(url, data=self.edit_instance_data)
        self.assertEqual(302, response.status_code)
        self.test_instance.refresh_from_db()
        self.assertEqual(self.test_instance.name, "new_instance_name")

    def test_instance_edit_standard_user(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        url = reverse('service_catalog:instance_edit', kwargs=self.args)
        response = self.client.post(url, data=self.edit_instance_data)
        # by default is not allowed
        self.assertEqual(403, response.status_code)
        # give permission to the team
        self.team_member_role.permissions.add(
            Permission.objects.get_by_natural_key(codename="rename_instance",
                                                  app_label="service_catalog",
                                                  model="instance"),
            Permission.objects.get_by_natural_key(codename="change_requester_on_instance",
                                                  app_label="service_catalog",
                                                  model="instance")
        )
        self.test_quota_scope.add_user_in_role(self.standard_user_2, self.team_member_role)
        self.test_quota_scope_team.add_user_in_role(self.standard_user_2, self.team_member_role)
        response = self.client.post(url, data=self.edit_instance_data)
        # by default is not allowed
        self.assertEqual(302, response.status_code)
        self.test_instance.refresh_from_db()
        self.assertEqual(self.test_instance.name, "new_instance_name")
        self.assertEqual(self.test_instance.requester, self.standard_user_2)

    def test_instance_edit_with_empty_spec(self):
        old_spec = copy(self.test_instance.spec)
        url = reverse('service_catalog:instance_edit', kwargs=self.args)
        self.edit_instance_data['spec'] = ''
        response = self.client.post(url, data=self.edit_instance_data)
        self.assertEqual(200, response.status_code)
        self.test_instance.refresh_from_db()
        self.assertEqual(self.test_instance.spec, old_spec)
        self.assertEqual(response.context['form'].errors['spec'][0],
                         'Please enter a valid JSON. Empty value is {} for JSON.')

        old_user_spec = copy(self.test_instance.spec)
        self.edit_instance_data['spec'] = json.dumps(self.json_spec)
        self.edit_instance_data['user_spec'] = ''
        response = self.client.post(url, data=self.edit_instance_data)
        self.assertEqual(200, response.status_code)
        self.test_instance.refresh_from_db()
        self.assertEqual(self.test_instance.spec, old_spec)
        self.assertEqual(response.context['form'].errors['user_spec'][0],
                         'Please enter a valid JSON. Empty value is {} for JSON.')

        self.assertEqual(self.test_instance.user_spec, old_user_spec)

    def test_instance_edit_with_empty_dict_spec(self):
        url = reverse('service_catalog:instance_edit', kwargs=self.args)
        self.edit_instance_data['spec'] = '{}'
        response = self.client.post(url, data=self.edit_instance_data)
        self.assertEqual(302, response.status_code)
        self.test_instance.refresh_from_db()
        self.assertEqual(self.test_instance.spec, {})

    def test_admin_can_delete_instance(self):
        request_id_list = [request.id for request in Request.objects.filter(instance=self.test_instance)]
        url = reverse('service_catalog:instance_delete', kwargs=self.args)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.client.post(url)
        self.assertFalse(Instance.objects.filter(id=self.test_instance.id).exists())
        for request_id in request_id_list:
            self.assertFalse(Request.objects.filter(id=request_id).exists())
