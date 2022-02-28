from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import Service, OperationType
from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.utils import check_data_in_dict


class TestApiServiceCreate(BaseTestRequest):

    def setUp(self):
        super(TestApiServiceCreate, self).setUp()
        self.post_data = {
            'name': "My new name",
            'description': "My new description",
            'billing_group_id': self.test_billing_group.id,
            'billing_group_is_shown': True,
            'billing_group_is_selectable': True,
            'billing_groups_are_restricted': False,
            'enabled': False,
        }
        self.get_service_details_url = reverse('api_service_list_create')

    def test_admin_post_service(self):
        response = self.client.post(self.get_service_details_url, data=self.post_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        check_data_in_dict(self, [self.post_data], [response.data])
        service = Service.objects.last()
        self.assertEqual(service.name, self.post_data['name'])
        self.assertEqual(service.billing_group_is_shown, self.post_data['billing_group_is_shown'])
        self.assertEqual(service.billing_group_is_selectable, self.post_data['billing_group_is_selectable'])
        self.assertEqual(service.billing_groups_are_restricted, self.post_data['billing_groups_are_restricted'])
        self.assertEqual(service.billing_group_id, self.post_data['billing_group_id'])

    def test_admin_cannot_post_on_service_not_full(self):
        self.post_data.pop('name')
        response = self.client.post(self.get_service_details_url, data=self.post_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_customer_cannot_post_service(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.post(self.get_service_details_url, data=self.post_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_post_service_when_logout(self):
        self.client.logout()
        response = self.client.post(self.get_service_details_url, data=self.post_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
