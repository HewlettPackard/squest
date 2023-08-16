from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import Request, RequestState
from tests.test_service_catalog.base_test_request import BaseTestRequestAPI


class TestApiRequestDelete(BaseTestRequestAPI):

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

    def test_customer_cannot_delete_non_owned_request_canceled(self):
        self.test_request_standard_user_2.state = RequestState.CANCELED
        self.test_request_standard_user_2.save()
        self.kwargs['pk'] = self.test_request_standard_user_2.id
        self.get_request_details_url = reverse('api_request_details', kwargs=self.kwargs)
        self.client.logout()
        self.client.force_login(user=self.standard_user)
        response = self.client.delete(self.get_request_details_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_delete_request_when_logout(self):
        self.client.logout()
        response = self.client.delete(self.get_request_details_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
