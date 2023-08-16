from rest_framework import status
from rest_framework.reverse import reverse

from resource_tracker_v2.api.serializers.resource_group_serializers import ResourceGroupSerializer
from resource_tracker_v2.models import ResourceGroup
from tests.test_resource_tracker_v2.base_test_resource_tracker_v2 import BaseTestResourceTrackerV2API


class TestResourceGroupAPIViews(BaseTestResourceTrackerV2API):

    def setUp(self):
        super(TestResourceGroupAPIViews, self).setUp()
        self._list_create_url = reverse('api_resourcegroup_list_create')
        self._details_url = reverse('api_resourcegroup_details', kwargs={'pk': self.cluster.id})

    def test_create_valid_resource_group(self):
        data = {
            "name": "new-resource-group-test",
            "tags": ["new_tag3", "new_tag4"]
        }
        number_resource_group_before = ResourceGroup.objects.all().count()
        response = self.client.post(self._list_create_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ResourceGroup.objects.latest('id').name, data["name"])
        self.assertEqual(number_resource_group_before + 1,
                         ResourceGroup.objects.all().count())

    def test_create_resource_group_name_exist_already(self):
        data = {
            "name": self.cluster.name,
            "tags": ["new_tag3", "new_tag4"]
        }
        response = self.client.post(self._list_create_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Resource Group With This Name Already Exists", response.data["name"][0].title())

    def test_resource_group_resources_list(self):
        response = self.client.get(self._list_create_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], ResourceGroup.objects.all().count())
        for resource_group in response.json()['results']:
            self.assertTrue("id" in resource_group)
            self.assertTrue("name" in resource_group)
            self.assertTrue("tags" in resource_group)

    def test_resource_group_list_filter_by_name(self):
        # test existing name
        testing_rg = ResourceGroup.objects.create(name="rg-test")
        url = self._list_create_url + f"?name={testing_rg.name}"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, response.data['count'])
        serializer = ResourceGroupSerializer(testing_rg)
        self.assertEqual(response.data['results'],  [serializer.data])

        # test non existing name
        url = self._list_create_url + f"?name=do_not_exist"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(0, response.data['count'])

    def test_update_resource_group(self):
        data = {
            "name": "updated",
            "tags": '["new_tag"]'
        }
        response = self.client.put(self._details_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cluster.refresh_from_db()
        self.assertEqual(self.cluster.name, "updated")
        self.assertEqual(self.cluster.tags.all().first().name, "new_tag")

    def test_delete_resource_group(self):
        id_to_delete = self.cluster.id
        response = self.client.delete(self._details_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ResourceGroup.objects.filter(id=id_to_delete))

    def test_get_resource_group_details(self):
        response = self.client.get(self._details_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("id" in response.json())
        self.assertTrue("name" in response.json())
        self.assertTrue("tags" in response.json())
        self.assertEqual(response.json()["id"], self.cluster.id)
        self.assertEqual(response.json()["name"], self.cluster.name)
