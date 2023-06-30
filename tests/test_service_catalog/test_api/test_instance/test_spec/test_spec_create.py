from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequestAPI
from tests.utils import check_data_in_dict


class TestApiSpecCreate(BaseTestRequestAPI):

    def setUp(self):
        super(TestApiSpecCreate, self).setUp()
        self.kwargs = {
            'pk': self.test_instance.id
        }
        self.expected_data = {
            "key1": "value1",
            "key2": "value2",
        }
        self.get_spec_details_url = reverse('api_instance_spec_details', kwargs=self.kwargs)
        self.expected_data_list = [self.expected_data]
        self.target_spec = "spec"  # used to determine if we check the content of test_instance.spec or test_instance.user_spec

    def test_admin_create_spec(self):
        if self.target_spec == "spec":
            self.assertEqual(self.test_instance.spec, {})
        else:
            self.assertEqual(self.test_instance.user_spec, {})
        response = self.client.post(self.get_spec_details_url, data=self.expected_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data_list = [response.data]
        check_data_in_dict(self, self.expected_data_list, data_list)
        self.test_instance.refresh_from_db()
        if self.target_spec == "spec":
            self.assertEqual(self.test_instance.spec, self.expected_data)
        else:
            self.assertEqual(self.test_instance.user_spec, self.expected_data)


    def test_cannot_create_spec_when_logout(self):
        self.client.logout()
        response = self.client.post(self.get_spec_details_url, data=self.expected_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
