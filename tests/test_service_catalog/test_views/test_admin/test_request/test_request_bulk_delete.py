from django.urls import reverse

from service_catalog.models import Request
from tests.test_service_catalog.base_test_request import BaseTestRequest


class RequestBulkDeleteTest(BaseTestRequest):
    def setUp(self):
        super(RequestBulkDeleteTest, self).setUp()
        self.request_to_delete_list = list()
        for x in range(5):
            self.request_to_delete_list.append(
                Request.objects.create(
                    fill_in_survey={},
                    instance=self.test_instance,
                    operation=self.create_operation_test,
                    user=self.standard_user
                ).id
            )
        self.data = {"selection": self.request_to_delete_list}
        self.url_confirm = reverse('service_catalog:request_bulk_delete_confirm')
        self.url_delete = reverse('service_catalog:request_bulk_delete')

    def test_admin_can_confirm_bulk_delete(self):
        response = self.client.post(self.url_confirm, data=self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set([request.id for request in response.context['object_list']]),
            set(self.request_to_delete_list)
        )

    def test_admin_get_message_on_confirm_bulk_delete_with_empty_data(self):
        response = self.client.post(self.url_confirm)
        self.assertEqual(response.status_code, 302)

    def test_user_cannot_confirm_bulk_delete(self):
        self.client.force_login(self.standard_user)
        response = self.client.post(self.url_confirm, data=self.data)
        self.assertEqual(response.status_code, 302)

    def test_cannot_confirm_bulk_delete_when_logout(self):
        self.client.logout()
        response = self.client.post(self.url_confirm, data=self.data)
        self.assertEqual(response.status_code, 302)

    def test_admin_can_bulk_delete(self):
        self.assertEqual(Request.objects.filter(id__in=self.request_to_delete_list).count(), 5)
        response = self.client.post(self.url_delete, data=self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Request.objects.filter(id__in=self.request_to_delete_list).count(), 0)

    def test_admin_get_message_on_bulk_delete_with_empty_data(self):
        response = self.client.post(self.url_delete)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Request.objects.filter(id__in=self.request_to_delete_list).count(), 5)

    def test_user_cannot_bulk_delete(self):
        self.client.force_login(self.standard_user)
        response = self.client.post(self.url_delete, data=self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Request.objects.filter(id__in=self.request_to_delete_list).count(), 5)

    def test_cannot_bulk_delete_when_logout(self):
        self.client.logout()
        response = self.client.post(self.url_delete, data=self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Request.objects.filter(id__in=self.request_to_delete_list).count(), 5)
