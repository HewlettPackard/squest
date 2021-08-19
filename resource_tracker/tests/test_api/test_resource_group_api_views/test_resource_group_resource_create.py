from rest_framework import status
from rest_framework.reverse import reverse

from resource_tracker.models import Resource
from resource_tracker.tests.test_api.base_test_api import BaseTestAPI
from service_catalog.models import Instance


class TestResourceGroupResourceCreate(BaseTestAPI):

    def setUp(self):
        super(TestResourceGroupResourceCreate, self).setUp()
        self.url = reverse('api_resource_group_resource_list_create', args=[self.rg_physical_servers.id])

    def _check_resource_created(self, data, executed_attribute_length, executed_text_attribute_length=0):
        number_resource_before = Resource.objects.filter(resource_group=self.rg_physical_servers).count()
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(number_resource_before + 1,
                         Resource.objects.filter(resource_group=self.rg_physical_servers).count())
        self.assertEqual(response.data['name'], 'new_resource')
        self.assertTrue("service_catalog_instance" in response.data)
        self.assertEqual(len(response.data['attributes']), executed_attribute_length)
        self.assertEqual(len(response.data['text_attributes']), executed_text_attribute_length)

    def test_create_valid_resource(self):
        data = {
            "name": "new_resource",
            "service_catalog_instance": None,
            "attributes": [
                {
                    "name": "CPU",
                    "value": "12"
                }
            ],
            "text_attributes": [
                {
                    "name": "Description",
                    "value": "My description"
                }
            ]
        }
        self._check_resource_created(data=data, executed_attribute_length=1, executed_text_attribute_length=1)

    def test_create_valid_resource_with_instance(self):
        test_instance = Instance.objects.create(name="test_instance")
        data = {
            "name": "new_resource",
            "service_catalog_instance": test_instance.id,
            "attributes": [
                {
                    "name": "CPU",
                    "value": "12"
                }
            ],
            "text_attributes": [
                {
                    "name": "Description",
                    "value": "My description"
                }
            ]
        }
        self._check_resource_created(data=data, executed_attribute_length=1, executed_text_attribute_length=1)

    def test_create_resource_with_non_valid_instance(self):
        data = {
            "name": "new_resource",
            "service_catalog_instance": 123456,
            "attributes": [
                {
                    "name": "CPU",
                    "value": "12"
                }
            ],
            "text_attributes": [
                {
                    "name": "Description",
                    "value": "My description"
                }
            ]
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_resource_with_multiple_attribute(self):
        data = {
            "name": "new_resource",
            "service_catalog_instance": None,
            "attributes": [
                {
                    "name": "CPU",
                    "value": "12"
                },
                {
                    "name": "memory",
                    "value": "20"
                }
            ],
            "text_attributes": [
                {
                    "name": "Description",
                    "value": "My description"
                },
                {
                    "name": "Another text",
                    "value": "My text"
                }
            ]
        }
        self._check_resource_created(data=data, executed_attribute_length=2, executed_text_attribute_length=2)

    def test_create_resource_twice(self):
        data = {
            "name": "new_resource",
            "service_catalog_instance": None,
            "attributes": [
                {
                    "name": "CPU",
                    "value": "12"
                },
                {
                    "name": "memory",
                    "value": "20"
                }
            ],
            "text_attributes": [
                {
                    "name": "Description",
                    "value": "My description"
                }
            ]
        }
        self._check_resource_created(data=data, executed_attribute_length=2, executed_text_attribute_length=1)
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_resource_twice_same_attribute(self):
        data = {
            "name": "new_resource",
            "service_catalog_instance": None,
            "attributes": [
                {
                    "name": "CPU",
                    "value": "12"
                },
                {
                    "name": "CPU",
                    "value": "20"
                }
            ],
            "text_attributes": [
                {
                    "name": "Description",
                    "value": "My description"
                },
                {
                    "name": "Another text",
                    "value": "My text"
                }
            ]
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_non_valid_resource(self):
        data = {
            "name": "new_resource",
            "service_catalog_instance": None,
            "attributes": [
                {
                    "name": "do_not_exist_attribute",
                    "value": "12"
                }
            ],
            "text_attributes": [
                {
                    "name": "Description",
                    "value": "My description"
                }
            ]
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_non_valid_resource_group(self):
        url = reverse('api_resource_group_resource_list_create', args=[123456])
        data = {
            "name": "new_resource",
            "service_catalog_instance": None,
            "attributes": [
                {
                    "name": "CPU",
                    "value": "12"
                }
            ],
            "text_attributes": [
                {
                    "name": "Description",
                    "value": "My description"
                }
            ]
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
