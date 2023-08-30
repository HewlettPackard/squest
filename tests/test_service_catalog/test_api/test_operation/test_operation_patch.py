from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequestAPI
from tests.utils import check_data_in_dict


class TestApiOperationPatch(BaseTestRequestAPI):

    def setUp(self):
        super(TestApiOperationPatch, self).setUp()
        self.patch_data = {
            'name': "My new name",
            'description': "My new description",
        }
        self.kwargs = {
            'pk': self.create_operation_test.id
        }
        self.get_operation_details_url = reverse('api_operation_details', kwargs=self.kwargs)
        self.expected_data = {
            'id': self.create_operation_test.id,
            'name': "My new name",
            'description': "My new description",
            'type': self.create_operation_test.type,
            'auto_accept': self.create_operation_test.auto_accept,
            'auto_process': self.create_operation_test.auto_process,
            'process_timeout_second': self.create_operation_test.process_timeout_second,
            'service': self.create_operation_test.service.id,
            'job_template': self.create_operation_test.job_template.id
        }

    def test_admin_patch_operation(self):
        response = self.client.patch(self.get_operation_details_url, data=self.patch_data,
                                     format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        check_data_in_dict(self, [self.expected_data], [response.data])

    def test_customer_cannot_patch_operation(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.patch(self.get_operation_details_url, data=self.patch_data,
                                     format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_patch_operation_when_logout(self):
        self.client.logout()
        response = self.client.patch(self.get_operation_details_url, data=self.patch_data,
                                     format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unset_job_template_of_create_operation_disable_the_service(self):
        self.assertTrue(self.service_test.enabled)
        self.patch_data['job_template'] = None
        self.client.patch(self.get_operation_details_url, data=self.patch_data,
                          format="json")
        self.service_test.refresh_from_db()
        self.assertFalse(self.service_test.can_be_enabled())
        self.assertFalse(self.service_test.enabled)
