from django.urls import reverse

from service_catalog.models import Request, Service, RequestMessage, Portfolio, Operation
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestCustomerCatalogViews(BaseTestRequest):

    def setUp(self):
        super(TestCustomerCatalogViews, self).setUp()
        self.client.login(username=self.standard_user, password=self.common_password)

    def test_customer_list_service_in_root(self):
        url = reverse('service_catalog:service_catalog_list')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertTrue("service_list" in response.context)
        self.assertEqual(len(response.context["service_list"]), Service.objects.filter(enabled=True).count())
        self.assertEqual(len(response.context["portfolio_list"]),
                         Portfolio.objects.filter(parent_portfolio=None).count())

    def test_customer_list_service_in_a_portfolio(self):
        self.service_test.parent_portfolio = self.portfolio_test_1
        self.service_test.save()
        url = reverse('service_catalog:service_catalog_list') + f"?parent_portfolio={self.portfolio_test_1.id}"
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertTrue("service_list" in response.context)
        self.assertEqual(len(response.context["service_list"]),
                         Service.objects.filter(enabled=True, parent_portfolio=self.portfolio_test_1).count())
        self.assertEqual(len(response.context["portfolio_list"]),
                         Portfolio.objects.filter(parent_portfolio=self.portfolio_test_1.id).count())

    def test_customer_can_list_service_catalog_enabled_service(self):
        self.service_test.enabled = False
        self.service_test.save()
        url = reverse('service_catalog:service_catalog_list')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["service_list"]), Service.objects.filter(enabled=True).count())

    def test_customer_cannot_access_service_list(self):
        url = reverse('service_catalog:service_list')
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

    def test_customer_service_request(self):
        args = {
            "service_id": self.service_test.id,
            "operation_id": self.create_operation_test.id
        }
        url = reverse('service_catalog:customer_service_request', kwargs=args)

        data = {
            "squest_instance_name": "instance_1",
            "text_variable": "text_value_1",
            "multiplechoice_variable": "text_value_2"
        }
        number_request_before = Request.objects.all().count()
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(number_request_before + 1, Request.objects.all().count())

    def test_customer_service_request_without_survey(self):
        args = {
            "service_id": self.service_test.id,
            "operation_id": self.create_operation_test.id
        }
        url = reverse('service_catalog:customer_service_request', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_create_request_with_a_comment(self):
        self.client.force_login(user=self.standard_user)
        args = {
            "service_id": self.service_test.id,
            "operation_id": self.create_operation_test.id
        }
        url = reverse('service_catalog:customer_service_request', kwargs=args)

        data = {
            "squest_instance_name": "instance_1",
            "text_variable": "text_value_1",
            "multiplechoice_variable": "text_value_2",
            "request_comment": "here_is_a_comment"
        }
        number_request_before = Request.objects.all().count()
        number_comment_before = RequestMessage.objects.all().count()
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(number_request_before + 1, Request.objects.all().count())
        self.assertEqual(number_comment_before + 1, RequestMessage.objects.all().count())

        created_request = Request.objects.latest('id')
        self.assertEqual(created_request.comments.count(), 1)
        self.assertNotIn("billing_group_id", created_request.fill_in_survey.keys())
        self.assertNotIn("request_comment", created_request.fill_in_survey.keys())
        self.assertEqual(created_request.comments.first().content, "here_is_a_comment")
        self.assertEqual(created_request.comments.first().sender, self.standard_user)

    def test_customer_cannot_create_request_on_admin_only_operation(self):
        admin_create_operation = Operation.objects.create(name="create admin",
                                                          service=self.service_test,
                                                          job_template=self.job_template_test,
                                                          is_admin_operation=True,
                                                          process_timeout_second=20)
        self.client.force_login(user=self.standard_user)
        args = {
            "service_id": self.service_test.id
        }
        url = reverse('service_catalog:create_operation_list', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        args["operation_id"] = admin_create_operation.id
        url = reverse('service_catalog:customer_service_request', kwargs=args)

        data = {
            "squest_instance_name": "instance_1",
            "text_variable": "text_value_1",
            "multiplechoice_variable": "text_value_2",
            "request_comment": "here_is_a_comment"
        }
        response = self.client.post(url, data=data)
        self.assertEqual(404, response.status_code)
