from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import OperationType
from tests.test_service_catalog.base_test_request import BaseTestRequestAPI


class TestApiOperationListInInstance(BaseTestRequestAPI):

    def setUp(self):
        super(TestApiOperationListInInstance, self).setUp()
        self.kwargs = {'instance_id': self.test_instance.id}
        self.get_operation_list_url = reverse('api_instance_operation_list', kwargs=self.kwargs)

    def test_admin_get_all_operations_of_the_instance(self):
        self._check_list()

    def test_customer_cannot_get_all_operations_of_non_own_instance(self):
        self.client.force_login(user=self.standard_user_2)
        self._check_list(status_expected=status.HTTP_404_NOT_FOUND)

    def test_cannot_get_operation_list_when_logout(self):
        self.client.logout()
        self._check_list(status_expected=status.HTTP_403_FORBIDDEN)

    def _check_list(self, status_expected=None):
        response_status = status_expected
        if status_expected is None:
            response_status = status.HTTP_200_OK
        response = self.client.get(self.get_operation_list_url)
        self.assertEqual(response.status_code, response_status)
        if response_status == status.HTTP_200_OK:
            self.assertEqual(response.data['count'],
                             self.test_instance.service.operations.exclude(type=OperationType.CREATE).count())

    def test_list_exclude_operation_with_when_condition(self):
        available_operation = self.test_instance.service.operations.exclude(type=OperationType.CREATE).count()

        # add a condition on the operation. We should not get it anymore in the list
        self.update_operation_test.when = "instance.user_spec.location=='grenoble'"
        self.update_operation_test.save()
        response = self.client.get(self.get_operation_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], available_operation - 1)

        # add the right spec to the instance to get the operation back in the list
        self.test_instance.user_spec = {
            "location": "grenoble"
        }
        self.test_instance.save()
        response = self.client.get(self.get_operation_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], available_operation)
