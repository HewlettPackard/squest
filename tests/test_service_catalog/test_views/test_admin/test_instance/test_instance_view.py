import json
from copy import copy

from django.urls import reverse

from service_catalog.models import Support, Instance, Request, InstanceState
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestAdminInstanceViews(BaseTestRequest):

    def setUp(self):
        super(TestAdminInstanceViews, self).setUp()
        self.args = {
            "instance_id": self.test_instance.id
        }
        self.json_spec = {
            "key1": "val1",
            "key2": "val2"
        }
        self.edit_instance_data = {
            "name": "new_instance_name",
            "service": self.service_test_2.id,
            "spoc": self.standard_user_2.id,
            "state": InstanceState.PROVISIONING,
            "billing_group": "",
            "spec": json.dumps(self.json_spec)
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
        url = reverse('service_catalog:instance_details', kwargs=self.args)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertTrue("instance" in response.context)
        self.assertEqual(self.test_instance.name, response.context["instance"].name)

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

    def test_admin_instance_new_support(self):
        url = reverse('service_catalog:instance_new_support', kwargs=self.args)
        data = {
            "title": "test_support",
            "content": "test_support_content"
        }
        number_support_before = Support.objects.all().count()
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(number_support_before + 1, Support.objects.all().count())

    def test_customer_cannot_create_new_support_on_non_own_instance(self):
        self.client.login(username=self.standard_user_2, password=self.common_password)
        url = reverse('service_catalog:instance_new_support', kwargs=self.args)
        data = {
            "title": "test_support",
            "content": "test_support_content"
        }
        number_support_before = Support.objects.all().count()
        response = self.client.post(url, data=data)
        self.assertEqual(403, response.status_code)
        self.assertEqual(number_support_before, Support.objects.all().count())

    def test_admin_get_instance_support_details(self):
        self.args['support_id'] = self.support_test.id
        url = reverse('service_catalog:instance_support_details', kwargs=self.args)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertTrue("support" in response.context)
        self.assertEqual(self.support_test.title, response.context["support"].title)

    def test_customer_cannot_get_instance_support_details_of_another_user(self):
        self.client.login(username=self.standard_user_2, password=self.common_password)
        self.args['support_id'] = self.support_test.id
        url = reverse('service_catalog:instance_support_details', kwargs=self.args)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

    def test_instance_edit(self):
        url = reverse('service_catalog:instance_edit', kwargs=self.args)

        response = self.client.post(url, data=self.edit_instance_data)
        self.assertEqual(302, response.status_code)
        self.test_instance.refresh_from_db()
        self.assertEqual(self.test_instance.name, "new_instance_name")

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

    def test_instance_edit_with_empty_dict_spec(self):
        url = reverse('service_catalog:instance_edit', kwargs=self.args)
        self.edit_instance_data['spec'] = '{}'
        response = self.client.post(url, data=self.edit_instance_data)
        self.assertEqual(302, response.status_code)
        self.test_instance.refresh_from_db()
        self.assertEqual(self.test_instance.spec, {})

    def test_customer_cannot_edit_instance(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        url = reverse('service_catalog:instance_edit', kwargs=self.args)
        response = self.client.post(url, data=self.edit_instance_data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(self.test_instance.name, "test_instance_1")

    def test_admin_can_delete_instance(self):
        request_id_list = [request.id for request in Request.objects.filter(instance=self.test_instance)]
        url = reverse('service_catalog:instance_delete', kwargs=self.args)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.client.post(url)
        self.assertFalse(Instance.objects.filter(id=self.test_instance.id).exists())
        for request_id in request_id_list:
            self.assertFalse(Request.objects.filter(id=request_id).exists())

    def test_customer_cannot_delete_instance(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        url = reverse('service_catalog:instance_delete', kwargs=self.args)
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        self.client.post(url)
        self.assertTrue(Instance.objects.filter(id=self.test_instance.id).exists())
