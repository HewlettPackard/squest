from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_resource_tracker.test_api.base_test_api import BaseTestAPI
from tests.utils import check_data_in_dict


class TestResourcePoolDetail(BaseTestAPI):

    def setUp(self):
        super(TestResourcePoolDetail, self).setUp()
        self.url = reverse('api_resource_pool_details',  args=[self.rp_vcenter.id])

    def test_resource_group_details(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("id" in response.json())
        self.assertTrue("name" in response.json())
        self.assertTrue("attribute_definitions" in response.json())
        self.assertTrue("tags" in response.json())
        self.assertEqual(response.json()["id"], self.rp_vcenter.id)
        self.assertEqual(response.json()["name"], self.rp_vcenter.name)
        self.assertEqual(len(response.json()["attribute_definitions"]),
                         self.rp_vcenter.attribute_definitions.all().count())
        expected_attributes = [
            {
                "name": "vCPU",
                "over_commitment_producers": 1.0,
                "over_commitment_consumers": 1.0
            },
            {
                "name": "Memory",
                "over_commitment_producers": 1.0,
                "over_commitment_consumers": 1.0
            }
        ]
        check_data_in_dict(self, expected_attributes, response.json()["attribute_definitions"])
