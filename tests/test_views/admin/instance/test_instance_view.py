import json

from django.urls import reverse

from service_catalog.models import Support
from tests.base_test_request import BaseTestRequest


class TestAdminInstanceViews(BaseTestRequest):

    def setUp(self):
        super(TestAdminInstanceViews, self).setUp()

    def test_get_instance_list(self):
        url = reverse('service_catalog:admin_instance_list')
        response = self.client.get(url)
        self.assertEquals(200, response.status_code)
        self.assertTrue("instances" in response.context)
        self.assertEquals(len(response.context["instances"].qs), 2)

    def test_customer_cannot_list_instance_from_admin_view(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        url = reverse('service_catalog:admin_instance_list')
        response = self.client.get(url)
        self.assertEquals(302, response.status_code)
        self.assertIsNone(response.context)

    def test_admin_can_get_details(self):
        args = {
            "instance_id": self.test_instance.id
        }
        url = reverse('service_catalog:admin_instance_details', kwargs=args)
        response = self.client.get(url)
        self.assertEquals(200, response.status_code)
        self.assertTrue("instance" in response.context)
        self.assertEquals(self.test_instance.name, response.context["instance"].name)

    def test_customer_cannot_get_details(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        args = {
            "instance_id": self.test_instance.id
        }
        url = reverse('service_catalog:admin_instance_details', kwargs=args)
        response = self.client.get(url)
        self.assertEquals(302, response.status_code)

    def test_admin_instance_new_support(self):
        args = {
            "instance_id": self.test_instance.id
        }
        url = reverse('service_catalog:admin_instance_new_support', kwargs=args)
        data = {
            "title": "test_support",
            "content": "test_support_content"
        }
        number_support_before = Support.objects.all().count()
        response = self.client.post(url, data=data)
        self.assertEquals(302, response.status_code)
        self.assertEquals(number_support_before + 1, Support.objects.all().count())

    def test_customer_cannot_create_new_support_from_admin(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        args = {
            "instance_id": self.test_instance.id
        }
        url = reverse('service_catalog:admin_instance_new_support', kwargs=args)
        data = {
            "title": "test_support",
            "content": "test_support_content"
        }
        number_support_before = Support.objects.all().count()
        response = self.client.post(url, data=data)
        self.assertEquals(302, response.status_code)
        self.assertEquals(number_support_before, Support.objects.all().count())

    def test_admin_get_instance_support_details(self):
        args = {
            "instance_id": self.test_instance.id,
            "support_id": self.support_test.id
        }
        url = reverse('service_catalog:admin_instance_support_details', kwargs=args)
        response = self.client.get(url)
        self.assertEquals(200, response.status_code)
        self.assertTrue("support" in response.context)
        self.assertEquals(self.support_test.title, response.context["support"].title)

    def test_customer_cannot_get_instance_support_details(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        args = {
            "instance_id": self.test_instance.id,
            "support_id": self.support_test.id
        }
        url = reverse('service_catalog:admin_instance_support_details', kwargs=args)
        response = self.client.get(url)
        self.assertEquals(302, response.status_code)
        self.assertIsNone(response.context)

    def test_admin_instance_edit(self):
        args = {
            "instance_id": self.test_instance.id,
        }
        url = reverse('service_catalog:admin_instance_edit', kwargs=args)
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
        url = reverse('service_catalog:admin_instance_edit', kwargs=args)
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
