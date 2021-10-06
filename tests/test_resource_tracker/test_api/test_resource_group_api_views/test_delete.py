from rest_framework import status
from rest_framework.reverse import reverse

from resource_tracker.models import ResourceGroup
from tests.test_resource_tracker.test_api.base_test_api import BaseTestAPI


class TestResourceGroupDelete(BaseTestAPI):

    def setUp(self):
        super(TestResourceGroupDelete, self).setUp()
        # get a resource to delete
        self.resource_to_delete_id = self.rg_physical_servers.id
        self.url = reverse('api_resource_group_details',  args=[self.resource_to_delete_id])

    def test_delete_resource_group(self):
        number_resource_before = ResourceGroup.objects.all().count()
        response = self.client.delete(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(number_resource_before - 1,
                         ResourceGroup.objects.all().count())
        self.assertFalse(ResourceGroup.objects.filter(id=self.resource_to_delete_id).exists())

    def test_delete_non_existing_resource_group(self):
        url = reverse('api_resource_group_details',  args=[999999])
        number_resource_before = ResourceGroup.objects.all().count()
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(number_resource_before,
                         ResourceGroup.objects.all().count())

    def test_customer_cannot_delete(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        response = self.client.delete(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
