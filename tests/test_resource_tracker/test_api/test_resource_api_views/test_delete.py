from rest_framework import status
from rest_framework.reverse import reverse

from resource_tracker.models import Resource
from tests.test_resource_tracker.test_api.base_test_api import BaseTestAPI


class TestResourceDelete(BaseTestAPI):

    def setUp(self):
        super(TestResourceDelete, self).setUp()
        # get a resource to delete
        self.resource_to_delete = Resource.objects.get(name="server-1")
        self.resource_to_delete_id = self.resource_to_delete.id
        self.url = reverse('api_resource_retrieve_delete',  args=[self.rg_physical_servers.id,
                                                                  self.resource_to_delete.id])

    def test_delete_resource(self):
        number_resource_before = Resource.objects.filter(resource_group=self.rg_physical_servers).count()
        response = self.client.delete(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(number_resource_before - 1,
                         Resource.objects.filter(resource_group=self.rg_physical_servers).count())
        self.assertFalse(Resource.objects.filter(id=self.resource_to_delete.id).exists())

    def _check_not_found(self, url):
        number_resource_before = Resource.objects.filter(resource_group=self.rg_physical_servers).count()
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(number_resource_before,
                         Resource.objects.filter(resource_group=self.rg_physical_servers).count())

    def test_delete_non_existing_resource_group(self):
        url = reverse('api_resource_retrieve_delete', args=[99999,
                                                            self.resource_to_delete.id])
        self._check_not_found(url)

    def test_delete_non_existing_resource(self):
        url = reverse('api_resource_retrieve_delete', args=[self.rg_physical_servers.id,
                                                            99999])
        self._check_not_found(url)
