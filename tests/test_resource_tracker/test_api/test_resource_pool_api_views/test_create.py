from rest_framework import status
from rest_framework.reverse import reverse
from taggit.models import Tag

from resource_tracker.models import ResourcePool, ResourcePoolAttributeDefinition
from tests.test_resource_tracker.test_api.base_test_api import BaseTestAPI


class TestResourcePoolCreate(BaseTestAPI):

    def setUp(self):
        super(TestResourcePoolCreate, self).setUp()
        self.url = reverse('api_resource_pool_list_create')

    def _check_resource_created(self, data):
        number_resource_pool_before = ResourcePool.objects.all().count()
        number_attribute_def_before = ResourcePoolAttributeDefinition.objects.all().count()
        added_att_def = len(data["attribute_definitions"])
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ResourcePool.objects.latest('id').name, data["name"])
        self.assertEqual(number_resource_pool_before + 1,
                         ResourcePool.objects.all().count())
        # the new attribute definition should have been added
        self.assertEqual(number_attribute_def_before + added_att_def,
                         ResourcePoolAttributeDefinition.objects.all().count())
        for attribute in data["attribute_definitions"]:
            last_inserted_attribute = ResourcePoolAttributeDefinition.objects.get(name=attribute["name"],
                                                                                  resource_pool=ResourcePool.objects.latest('id'))
            self.assertEqual(attribute["over_commitment_producers"], last_inserted_attribute.over_commitment_producers)
            self.assertEqual(attribute["over_commitment_consumers"], last_inserted_attribute.over_commitment_consumers)

    def test_create_valid_resource_pool(self):
        data = {
            "name": "new-resource-pool-test",
            "attribute_definitions": [{"name": "vCPU",
                                       "over_commitment_producers": 1.5,
                                       "over_commitment_consumers": 2.2
                                       },
                                      {"name": "Memory",
                                       "over_commitment_producers": 1.3,
                                       "over_commitment_consumers": 2.6
                                       }
                                      ],
            "tags": ["new_tag1", "new_tag2"]
        }
        self._check_resource_created(data=data)

    def test_create_resource_pool_bad_overcommitment(self):
        data = {
            "name": "new-resource-pool-test",
            "attribute_definitions": [{"name": "vCPU",
                                       "over_commitment_producers": "text",
                                       "over_commitment_consumers": 2.0
                                       }
                                      ],
            "tags": ["new_tag1", "new_tag2"]
        }
        number_resource_pool_before = ResourcePool.objects.all().count()
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(number_resource_pool_before,
                         ResourcePool.objects.all().count())

    def test_create_resource_pool_same_tag(self):
        number_tag_before = Tag.objects.all().count()
        data = {
            "name": "new-resource-pool-test",
            "attribute_definitions": [],
            "tags": ["new_tag1", "new_tag2"]
        }
        self._check_resource_created(data=data)
        self.assertEqual(number_tag_before + 2,
                         Tag.objects.all().count())
        data = {
            "name": "new-resource-pool-test-2",
            "attribute_definitions": [],
            "tags": ["new_tag1", "new_tag3"]
        }
        self._check_resource_created(data=data)
        self.assertEqual(number_tag_before + 3,
                         Tag.objects.all().count())
