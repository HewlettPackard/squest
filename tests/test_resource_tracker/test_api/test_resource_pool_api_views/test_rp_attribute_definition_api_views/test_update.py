from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_resource_tracker.test_api.base_test_api import BaseTestAPI


class TestResourcePoolAttributeDefinitionUpdate(BaseTestAPI):

    def setUp(self):
        super(TestResourcePoolAttributeDefinitionUpdate, self).setUp()
        self.url = reverse('api_resource_pool_attribute_definition_retrieve_update_delete',
                           args=[self.rp_vcenter.id,
                                 self.rp_vcenter_vcpu_attribute.id])

    def _test_update(self, data):
        resource_pool_id = self.rp_vcenter_vcpu_attribute.resource_pool.id
        response = self.client.put(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.rp_vcenter_vcpu_attribute.refresh_from_db()
        self.assertEqual(self.rp_vcenter_vcpu_attribute.name, data["name"])
        self.assertEqual(self.rp_vcenter_vcpu_attribute.resource_pool.id, resource_pool_id)

        if "over_commitment_producers" in data:
            self.assertEqual(self.rp_vcenter_vcpu_attribute.over_commitment_producers,
                             data["over_commitment_producers"])
        else:
            self.assertEqual(self.rp_vcenter_vcpu_attribute.over_commitment_producers,
                             1.0)

        if "over_commitment_consumers" in data:
            self.assertEqual(self.rp_vcenter_vcpu_attribute.over_commitment_consumers,
                             data["over_commitment_consumers"])
        else:
            self.assertEqual(self.rp_vcenter_vcpu_attribute.over_commitment_consumers,
                             1.0)

    def test_rp_attribute_definition_update(self):
        data = {
            "id": self.rg_physical_servers_cpu_attribute.id,
            "resource_pool": self.rp_vcenter.id,
            "name": "new_name",
            "over_commitment_producers": 3.0,
            "over_commitment_consumers": 4.0
        }
        self._test_update(data)

    def test_rp_attribute_definition_update_np_over_commitment(self):
        data = {
            "id": self.rg_physical_servers_cpu_attribute.id,
            "resource_pool": self.rp_vcenter.id,
            "name": "new_name"
        }
        self._test_update(data)

    def test_rp_attribute_definition_update_np_resource_pool_id_given(self):
        data = {
            "id": self.rg_physical_servers_cpu_attribute.id,
            "name": "new_name"
        }
        self._test_update(data)
