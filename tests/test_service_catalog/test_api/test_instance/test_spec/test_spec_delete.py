from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.utils import check_data_in_dict


class TestApiSpecDelete(BaseTestRequest):

    def setUp(self):
        super(TestApiSpecDelete, self).setUp()
        self.kwargs = {
            'pk': self.test_instance.id
        }
        self.expected_data = {}
        self.current_spec = {
            'spec_key1': "spec_value1",
            'spec_key2': "spec_value2",
        }
        self.current_user_spec = {
            'user_spec_key1': "user_spec_value1",
            'user_spec_key2': "user_spec_value2",
        }
        self.test_instance.spec = self.current_spec
        self.test_instance.user_spec = self.current_user_spec
        self.test_instance.save()
        self.get_spec_create_url = reverse('api_instance_spec_details', kwargs=self.kwargs)
        self.expected_data_list = [self.expected_data]
        self.target_spec = "spec"

    def test_admin_delete_spec(self):
        if self.target_spec == "spec":
            self.assertEqual(self.test_instance.spec, self.current_spec)
        else:
            self.assertEqual(self.test_instance.user_spec, self.current_user_spec)
        response = self.client.delete(self.get_spec_create_url, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        data_list = [response.data]
        check_data_in_dict(self, self.expected_data_list, data_list)
        self.test_instance.refresh_from_db()
        if self.target_spec == "spec":
            self.assertEqual(self.test_instance.spec, {})
        else:
            self.assertEqual(self.test_instance.user_spec, {})


    def test_cannot_delete_spec_when_logout(self):
        self.client.logout()
        response = self.client.delete(self.get_spec_create_url, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
