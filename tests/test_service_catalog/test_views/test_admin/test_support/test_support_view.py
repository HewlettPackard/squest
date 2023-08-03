from django.urls import reverse

from service_catalog.models import Support
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestAdminSupportViews(BaseTestRequest):

    def setUp(self):
        super(TestAdminSupportViews, self).setUp()
        self.url = reverse('service_catalog:support_list')

    def test_get_support_list(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["table"].data.data), 2)


    def test_cannot_get_support_list_when_logout(self):
        self.client.logout()
        url = reverse('service_catalog:support_list')
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)

    def test_admin_get_support_details(self):
        args = dict()
        args['instance_id'] = self.support_test.instance.id
        args['pk'] = self.support_test.id
        url = reverse('service_catalog:support_details', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertTrue("support" in response.context)
        self.assertEqual(self.support_test.title, response.context["support"].title)


    def test_customer_cannot_get_support_details_of_another_user(self):
        self.client.login(username=self.standard_user_2, password=self.common_password)
        args = dict()
        args['instance_id'] = self.support_test.instance.id
        args['pk'] = self.support_test.id
        url = reverse('service_catalog:support_details', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)


    def test_admin_support_create(self):
        args = dict()
        args['instance_id'] = self.support_test.instance.id
        url = reverse('service_catalog:support_create', kwargs=args)
        data = {
            "title": "test_support",
            "content": "test_support_content"
        }
        number_support_before = Support.objects.all().count()
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(number_support_before + 1, Support.objects.all().count())
