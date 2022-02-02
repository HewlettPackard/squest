from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.test_api.test_instance.test_spec.test_spec_details import TestApiSpecDetails


class TestApiUserSpecDetails(TestApiSpecDetails):

    def setUp(self):
        super(TestApiUserSpecDetails, self).setUp()
        self.get_spec_details_url = reverse('api_instance_user_spec_details', kwargs=self.kwargs)
        self.expected_data_list = [self.current_user_spec]
        self.target_spec = "user-spec"

    def test_admin_get_user_spec_detail(self):
        self.test_admin_get_spec_detail()

    def test_customer_can_get_user_spec_detail(self):
        self.client.force_login(user=self.standard_user)
        self.test_admin_get_spec_detail()

    def test_customer_cannot_get_user_spec_non_owned_instance(self):
        self.client.force_login(user=self.standard_user_2)
        response = self.client.get(self.get_spec_details_url, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_get_spec_details_when_logout(self):
        self.client.logout()
        response = self.client.get(self.get_spec_details_url, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
