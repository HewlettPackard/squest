from copy import copy

from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import InstanceState
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestInstanceUpdate(BaseTestRequest):

    def setUp(self):
        super(TestInstanceUpdate, self).setUp()
        self.url = reverse('api_instance_details', args=[self.test_instance.id])
        self.update_data = {
            "name": "new_name",
            "service": self.service_test_2.id,
            "requester": self.standard_user_2.id,
            "state": InstanceState.PROVISIONING,
            "billing_group": self.test_billing_group.id,
            "spec": {
                "key1": "val1",
                "key2": "val2"
            }
        }

    def test_update_instance(self):
        response = self.client.put(self.url, data=self.update_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.test_instance.refresh_from_db()
        expected_spec = {
            "key1": "val1",
            "key2": "val2"
        }
        self.assertDictEqual(self.test_instance.spec, expected_spec)
        self.assertEqual(self.test_instance.billing_group.id, self.update_data["billing_group"])
        self.assertEqual(self.test_instance.name, "new_name")

    def test_update_instance_with_empty_spec(self):
        old_name = copy(self.test_instance.name)
        old_spec = copy(self.test_instance.spec)
        self.update_data['spec'] = None
        response = self.client.put(self.url, data=self.update_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.test_instance.refresh_from_db()
        self.assertDictEqual(self.test_instance.spec, old_spec)
        self.assertEqual(self.test_instance.name, old_name)

    def test_update_instance_with_empty_dict_spec(self):
        self.update_data['spec'] = dict()
        response = self.client.put(self.url, data=self.update_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.test_instance.refresh_from_db()
        self.assertDictEqual(self.test_instance.spec, {})
        self.assertEqual(self.test_instance.name, "new_name")

    def test_non_admin_cannot_update(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.put(self.url, data=self.update_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_update_when_logout(self):
        self.client.logout()
        response = self.client.put(self.url, data=self.update_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
