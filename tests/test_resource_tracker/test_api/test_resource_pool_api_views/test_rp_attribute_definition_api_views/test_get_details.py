from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_resource_tracker.test_api.base_test_api import BaseTestAPI


class TestResourcePoolAttributeDefinitionDetail(BaseTestAPI):

    def setUp(self):
        super(TestResourcePoolAttributeDefinitionDetail, self).setUp()
        self.url = reverse('api_resource_pool_attribute_definition_retrieve_update_delete',
                           args=[self.rp_vcenter.id,
                                 self.rp_vcenter_vcpu_attribute.id])

    def test_attribute_definition_details(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("id" in response.json())
        self.assertTrue("name" in response.json())
        self.assertTrue("over_commitment_producers" in response.json())
        self.assertTrue("over_commitment_consumers" in response.json())
        self.assertTrue("resource_pool" in response.json())
        self.assertEqual(response.json()["id"], self.rp_vcenter_vcpu_attribute.id)
        self.assertEqual(response.json()["name"], self.rp_vcenter_vcpu_attribute.name)
        self.assertEqual(response.json()["over_commitment_producers"],
                         self.rp_vcenter_vcpu_attribute.over_commitment_producers)
        self.assertEqual(response.json()["over_commitment_consumers"],
                         self.rp_vcenter_vcpu_attribute.over_commitment_consumers)
        self.assertEqual(response.json()["resource_pool"], self.rp_vcenter_vcpu_attribute.resource_pool.id)
