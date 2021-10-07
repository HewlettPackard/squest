from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import InstanceState, Instance
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestInstanceCreate(BaseTestRequest):

    def setUp(self):
        super(TestInstanceCreate, self).setUp()
        self.url = reverse('api_admin_instance_list')

    def _test_create(self, data, expected):
        instance_count = Instance.objects.count()
        response = self.client.post(self.url, data=data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(instance_count + 1, Instance.objects.count())
        expected["id"] = response.data["id"]
        self.assertEqual(response.data, expected)

    def test_instance_create_all_field(self):
        data = {
            "name": "instance_create_test_1",
            "service": self.service_test_2.id,
            "spoc": self.standard_user_2.id,
            "state": InstanceState.AVAILABLE,
            "billing_group": None,
            "spec": {
                "key1": "val1",
                "key2": "val2"
            }
        }
        expected = {'state': 'AVAILABLE',
                    'name': 'instance_create_test_1',
                    'spec': {'key1': 'val1', 'key2': 'val2'},
                    'service': self.service_test_2.id,
                    'spoc': self.standard_user_2.id,
                    'billing_group': None}
        self._test_create(data, expected)

    def test_instance_create_spec_empty_dict(self):
        data = {
            "name": "instance_create_test_2",
            "service": self.service_test_2.id,
            "spoc": self.standard_user_2.id,
            "state": InstanceState.UPDATING,
            "billing_group": None,
            "spec": {}
        }
        expected = {'state': 'UPDATING',
                    'name': 'instance_create_test_2',
                    'spec': {},
                    'service': self.service_test_2.id,
                    'spoc': self.standard_user_2.id,
                    'billing_group': None}
        self._test_create(data, expected)

    def test_instance_create_no_service(self):
        data = {
            "name": "instance_create_test_3",
            "service": None,
            "spoc": self.standard_user_2.id,
            "state": InstanceState.PROVISIONING,
            "billing_group": None,
            "spec": {
            }
        }
        expected = {'state': 'PROVISIONING',
                    'name': 'instance_create_test_3',
                    'spec': {},
                    'service': None,
                    'spoc': self.standard_user_2.id,
                    'billing_group': None}
        self._test_create(data, expected)
