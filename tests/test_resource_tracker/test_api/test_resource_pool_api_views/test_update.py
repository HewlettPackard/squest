from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_resource_tracker.test_api.base_test_api import BaseTestAPI


class TestResourcePoolUpdate(BaseTestAPI):

    def setUp(self):
        super(TestResourcePoolUpdate, self).setUp()
        self.url = reverse('api_resource_pool_details',  args=[self.rp_vcenter.id])

    def test_update(self):
        """
        Update is partial. attribute_definitions are not handled
        """
        data = {
            "name": "updated",
            "tags": ["new_tag"]
        }
        response = self.client.put(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.rp_vcenter.refresh_from_db()
        self.assertEqual(self.rp_vcenter.name, "updated")
        self.assertEqual(self.rp_vcenter.tags.all().first().name, "new_tag")
