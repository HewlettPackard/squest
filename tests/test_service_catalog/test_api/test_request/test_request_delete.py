from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import Request, RequestState
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestApiRequestDelete(BaseTestRequest):

    def setUp(self):
        super(TestApiRequestDelete, self).setUp()
        self.test_request_standard_user_1 = Request.objects.create(
            fill_in_survey={},
            instance=self.test_instance,
            operation=self.create_operation_test,
            user=self.standard_user
        )
        self.test_request_standard_user_2 = Request.objects.create(
            fill_in_survey={},
            instance=self.test_instance_2,
            operation=self.create_operation_test,
            user=self.standard_user_2
        )
        self.request_to_delete_id = self.test_request_standard_user_1.id
        self.kwargs = {
            'pk': self.test_request_standard_user_1.id
        }
        self.get_request_details_url = reverse('api_request_details', kwargs=self.kwargs)

    def test_admin_delete_request(self):
        request_count = Request.objects.count()
        response = self.client.delete(self.get_request_details_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(request_count - 1, Request.objects.count())
        self.assertFalse(Request.objects.filter(id=self.request_to_delete_id).exists())

    def test_customer_cannot_delete_his_request_not_canceled(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.delete(self.get_request_details_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(
            "Request state must be 'CANCELED' to delete this request." in response.rendered_content.decode("utf-8"))

    def test_customer_delete_his_request_canceled(self):
        self.test_request_standard_user_1.state = RequestState.CANCELED
        self.test_request_standard_user_1.save()
        request_count = Request.objects.count()
        self.client.force_login(user=self.standard_user)
        response = self.client.delete(self.get_request_details_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(request_count - 1, Request.objects.count())
        self.assertFalse(Request.objects.filter(id=self.request_to_delete_id).exists())

    def test_customer_cannot_delete_non_owned_request_not_canceled(self):
        self.client.force_login(user=self.standard_user)
        self.kwargs['pk'] = self.test_request_standard_user_2.id
        self.get_request_details_url = reverse('api_request_details', kwargs=self.kwargs)
        response = self.client.delete(self.get_request_details_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_customer_cannot_delete_non_owned_request_canceled(self):
        self.test_request_standard_user_2.state = RequestState.CANCELED
        self.test_request_standard_user_2.save()
        self.kwargs['pk'] = self.test_request_standard_user_2.id
        self.get_request_details_url = reverse('api_request_details', kwargs=self.kwargs)
        self.client.logout()
        self.client.force_login(user=self.standard_user)
        response = self.client.delete(self.get_request_details_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_delete_request_when_logout(self):
        self.client.logout()
        response = self.client.delete(self.get_request_details_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
