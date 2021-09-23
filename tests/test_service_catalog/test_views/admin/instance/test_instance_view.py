import json

from django.urls import reverse

from service_catalog.models import Support, Instance, Request
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestAdminInstanceViews(BaseTestRequest):

    def setUp(self):
        super(TestAdminInstanceViews, self).setUp()

    def test_get_instance_list(self):
        url = reverse('service_catalog:instance_list')
        response = self.client.get(url)
        self.assertEquals(200, response.status_code)
        self.assertEquals(len(response.context["table"].data.data), 2)

    def test_cannot_get_instance_list_when_logout(self):
        self.client.logout()
        url = reverse('service_catalog:instance_list')
        response = self.client.get(url)
        self.assertEquals(302, response.status_code)

    def test_admin_can_get_details(self):
        args = {
            "instance_id": self.test_instance.id
        }
        url = reverse('service_catalog:instance_details', kwargs=args)
        response = self.client.get(url)
        self.assertEquals(200, response.status_code)
        self.assertTrue("instance" in response.context)
        self.assertEquals(self.test_instance.name, response.context["instance"].name)

    def test_cannot_get_instance_details_when_logout(self):
        self.client.login(username=self.standard_user_2, password=self.common_password)
        args = {
            "instance_id": self.test_instance.id
        }
        url = reverse('service_catalog:instance_details', kwargs=args)
        response = self.client.get(url)
        self.assertEquals(403, response.status_code)

    def test_customer_cannot_get_details_on_non_own_instance(self):
        self.client.login(username=self.standard_user_2, password=self.common_password)
        args = {
            "instance_id": self.test_instance.id
        }
        url = reverse('service_catalog:instance_details', kwargs=args)
        response = self.client.get(url)
        self.assertEquals(403, response.status_code)

    def test_admin_instance_new_support(self):
        args = {
            "instance_id": self.test_instance.id
        }
        url = reverse('service_catalog:instance_new_support', kwargs=args)
        data = {
            "title": "test_support",
            "content": "test_support_content"
        }
        number_support_before = Support.objects.all().count()
        response = self.client.post(url, data=data)
        self.assertEquals(302, response.status_code)
        self.assertEquals(number_support_before + 1, Support.objects.all().count())

    def test_customer_cannot_create_new_support_on_non_own_instance(self):
        self.client.login(username=self.standard_user_2, password=self.common_password)
        args = {
            "instance_id": self.test_instance.id
        }
        url = reverse('service_catalog:instance_new_support', kwargs=args)
        data = {
            "title": "test_support",
            "content": "test_support_content"
        }
        number_support_before = Support.objects.all().count()
        response = self.client.post(url, data=data)
        self.assertEquals(403, response.status_code)
        self.assertEquals(number_support_before, Support.objects.all().count())

    def test_admin_get_instance_support_details(self):
        args = {
            "instance_id": self.test_instance.id,
            "support_id": self.support_test.id
        }
        url = reverse('service_catalog:instance_support_details', kwargs=args)
        response = self.client.get(url)
        self.assertEquals(200, response.status_code)
        self.assertTrue("support" in response.context)
        self.assertEquals(self.support_test.title, response.context["support"].title)

    def test_customer_cannot_get_instance_support_details_of_another_user(self):
        self.client.login(username=self.standard_user_2, password=self.common_password)
        args = {
            "instance_id": self.test_instance.id,
            "support_id": self.support_test.id
        }
        url = reverse('service_catalog:instance_support_details', kwargs=args)
        response = self.client.get(url)
        self.assertEquals(403, response.status_code)

    def test_instance_edit(self):
        args = {
            "instance_id": self.test_instance.id,
        }
        url = reverse('service_catalog:instance_edit', kwargs=args)
        json_spec = {
                "key1": "val1",
                "key2": "val2"
            }
        data = {
            "name": "new_instance_name",
            "spec": json.dumps(json_spec)
        }
        response = self.client.post(url, data=data)
        self.assertEquals(302, response.status_code)
        self.test_instance.refresh_from_db()
        self.assertEquals(self.test_instance.name, "new_instance_name")

    def test_customer_cannot_edit_instance(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        args = {
            "instance_id": self.test_instance.id,
        }
        url = reverse('service_catalog:instance_edit', kwargs=args)
        json_spec = {
            "key1": "val1",
            "key2": "val2"
        }
        data = {
            "name": "new_instance_name",
            "spec": json.dumps(json_spec)
        }
        response = self.client.post(url, data=data)
        self.assertEquals(302, response.status_code)
        self.assertEquals(self.test_instance.name, "test_instance_1")

    def test_admin_can_delete_instance(self):
        args = {
            'instance_id': self.test_instance.id
        }
        request_id_list = [request.id for request in Request.objects.filter(instance=self.test_instance)]
        url = reverse('service_catalog:instance_delete', kwargs=args)
        response = self.client.get(url)
        self.assertEquals(200, response.status_code)
        self.client.post(url)
        self.assertFalse(Instance.objects.filter(id=self.test_instance.id).exists())
        for request_id in request_id_list:
            self.assertFalse(Request.objects.filter(id=request_id).exists())

    def test_customer_cannot_delete_instance(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        args = {
            'instance_id': self.test_instance.id
        }
        url = reverse('service_catalog:instance_delete', kwargs=args)
        response = self.client.get(url)
        self.assertEquals(302, response.status_code)
        self.client.post(url)
        self.assertTrue(Instance.objects.filter(id=self.test_instance.id).exists())
