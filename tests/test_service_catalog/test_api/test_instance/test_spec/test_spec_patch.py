from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequestAPI
from tests.utils import check_data_in_dict


class TestApiSpecPatch(BaseTestRequestAPI):

    def setUp(self):
        super(TestApiSpecPatch, self).setUp()
        self.kwargs = {
            'pk': self.test_instance.id
        }
        self.current_spec = {
            'spec_key1': "spec_value1",
            'spec_key2': "spec_value2",
        }
        self.current_user_spec = {
            'user_spec_key1': "user_spec_value1",
            'user_spec_key2': "user_spec_value2",
        }
        self.expected_spec = {
            'spec_key1': "spec_value1_updated",
            'spec_key2': "spec_value2",
        }
        self.expected_user_spec = {
            'user_spec_key1': "user_spec_value1_updated",
            'user_spec_key2': "user_spec_value2",
        }

        self.test_instance.spec = self.current_spec
        self.test_instance.user_spec = self.current_user_spec
        self.test_instance.save()
        self.get_spec_details_url = reverse('api_instance_spec_details', kwargs=self.kwargs)
        self.target_spec = "spec"
        self.expected_data = self.expected_spec

    def test_admin_patch_spec(self):
        if self.target_spec == "spec":
            self.assertEqual(self.test_instance.spec, self.current_spec)
            response = self.client.patch(self.get_spec_details_url,
                                         data=self.expected_spec,
                                         format="json")
        else:
            self.assertEqual(self.test_instance.user_spec, self.current_user_spec)
            response = self.client.patch(self.get_spec_details_url,
                                         data=self.expected_user_spec,
                                         format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data_list = [response.data]
        check_data_in_dict(self, [self.expected_data], data_list)
        self.test_instance.refresh_from_db()
        if self.target_spec == "spec":
            self.assertEqual(self.test_instance.spec, self.expected_data)
        else:
            self.assertEqual(self.test_instance.user_spec, self.expected_data)

    def _check_403_forbidden(self):
        if self.target_spec == "spec":
            self.assertEqual(self.test_instance.spec, self.current_spec)
            response = self.client.patch(self.get_spec_details_url,
                                         data=self.expected_spec,
                                         format="json")
        else:
            self.assertEqual(self.test_instance.user_spec, self.current_user_spec)
            response = self.client.patch(self.get_spec_details_url,
                                         data=self.expected_user_spec,
                                         format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        if self.target_spec == "spec":
            self.assertEqual(self.test_instance.spec, self.current_spec)
        else:
            self.assertEqual(self.test_instance.user_spec, self.current_user_spec)


    def test_cannot_patch_spec_when_logout(self):
        self.client.logout()
        self._check_403_forbidden()
