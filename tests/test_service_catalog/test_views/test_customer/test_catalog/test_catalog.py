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
        self.assertEqual(200, response.status_code)

    def test_customer_service_request(self):
        args = {
            "service_id": self.service_test.id,
            "operation_id": self.create_operation_test.id
        }
        url = reverse('service_catalog:request_service', kwargs=args)

        data_form1 = {
            "0-name": "instance_1",
            "0-quota_scope": self.test_quota_scope.id,
            "service_request_wizard_view-current_step": "0",
        }
        data_form2 = {
            "1-text_variable": "text_value_1",
            "1-multiplechoice_variable": "text_value_2",
            "service_request_wizard_view-current_step": "1",
        }
        number_request_before = Request.objects.all().count()
        STEPS_DATA = [data_form1, data_form2]
        for step, data_step in enumerate(STEPS_DATA, 1):
            response = self.client.post(url, data=data_step)
            if step == len(STEPS_DATA):
                self.assertEqual(302, response.status_code)
                self.assertEqual(number_request_before + 1, Request.objects.all().count())
            else:
                self.assertEqual(response.status_code, 200)

    def test_customer_service_request_without_survey(self):
        args = {
            "service_id": self.service_test.id,
            "operation_id": self.create_operation_test.id
        }
        url = reverse('service_catalog:request_service', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_create_request_with_a_comment(self):
        self.client.force_login(user=self.standard_user)
        args = {
            "service_id": self.service_test.id,
            "operation_id": self.create_operation_test.id
        }
        url = reverse('service_catalog:request_service', kwargs=args)

        data_form1 = {
            "0-name": "instance_1",
            "0-quota_scope": self.test_quota_scope.id,
            "service_request_wizard_view-current_step": "0",
        }
        data_form2 = {
            "1-text_variable": "text_value_1",
            "1-multiplechoice_variable": "text_value_2",
            "1-request_comment": "here_is_a_comment",
            "service_request_wizard_view-current_step": "1",
        }

        STEPS_DATA = [data_form1, data_form2]
        number_request_before = Request.objects.all().count()
        number_comment_before = RequestMessage.objects.all().count()

        for step, data_step in enumerate(STEPS_DATA, 1):
            response = self.client.post(url, data=data_step)

            if step == len(STEPS_DATA):
                self.assertEqual(302, response.status_code)
                self.assertEqual(number_request_before + 1, Request.objects.all().count())
                self.assertEqual(number_comment_before + 1, RequestMessage.objects.all().count())
            else:
                self.assertEqual(response.status_code, 200)

        created_request = Request.objects.latest('id')
        self.assertEqual(created_request.comments.count(), 1)
        self.assertNotIn("quota_scope_id", created_request.fill_in_survey.keys())
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
        self.assertEqual(response.status_code, 200)

        args["operation_id"] = admin_create_operation.id
        url = reverse('service_catalog:request_service', kwargs=args)

        data_form1 = {
            "0-name": "instance_1",
            "0-quota_scope": self.test_quota_scope.id,
            "service_request_wizard_view-current_step": "0",
        }
        data_form2 = {
            "1-text_variable": "text_value_1",
            "1-multiplechoice_variable": "text_value_2",
            "1-request_comment": "here_is_a_comment",
            "service_request_wizard_view-current_step": "1",
        }
        STEPS_DATA = [data_form1, data_form2]
        for step, data_step in enumerate(STEPS_DATA, 1):
            response = self.client.post(url, data=data_step)
            self.assertEqual(403, response.status_code)
