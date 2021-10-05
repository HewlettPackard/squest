from rest_framework import status
from rest_framework.reverse import reverse
from taggit.models import Tag

from resource_tracker.models import ResourceGroup, ResourceGroupAttributeDefinition, \
    ResourceGroupTextAttributeDefinition
from tests.test_resource_tracker.test_api.base_test_api import BaseTestAPI


class TestResourceGroupCreate(BaseTestAPI):

    def setUp(self):
        super(TestResourceGroupCreate, self).setUp()
        self.url = reverse('api_resource_group_list_create')

    def _check_resource_created(self, data):
        number_resource_group_before = ResourceGroup.objects.all().count()
        number_attribute_def_before = ResourceGroupAttributeDefinition.objects.all().count()
        number_text_attribute_def_before = ResourceGroupTextAttributeDefinition.objects.all().count()
        added_att_def = len(data["attribute_definitions"])
        added_text_att_def = len(data["text_attribute_definitions"])

        response = self.client.post(self.url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ResourceGroup.objects.latest('id').name, data["name"])
        self.assertEqual(number_resource_group_before + 1,
                         ResourceGroup.objects.all().count())
        # the new attribute definition should have been added
        self.assertEqual(number_attribute_def_before + added_att_def,
                         ResourceGroupAttributeDefinition.objects.all().count())
        self.assertEqual(number_text_attribute_def_before + added_text_att_def,
                         ResourceGroupTextAttributeDefinition.objects.all().count())

    def test_create_valid_resource_group(self):
        data = {
            "name": "new-resource-group-test",
            "attribute_definitions": [{"name": "CPU",
                                       "consume_from": None,
                                       "produce_for": self.rp_vcenter_vcpu_attribute.id,
                                       "help_text": "test_help"
                                       },
                                      {"name": "Memory",
                                       "consume_from": None,
                                       "produce_for": self.rp_vcenter_memory_attribute.id,
                                       "help_text": None
                                       }
                                      ],
            "text_attribute_definitions": [{"name": "text_att_test"}],
            "tags": ["new_tag3", "new_tag4"]
        }
        self._check_resource_created(data=data)

    def test_create_resource_group_non_valid_producer(self):
        data = {
            "name": "new-resource-group-test",
            "attribute_definitions": [{"name": "CPU",
                                       "consume_from": None,
                                       "produce_for": 999999,
                                       "help_text": "test_help"
                                       },
                                      {"name": "Memory",
                                       "consume_from": None,
                                       "produce_for": 999999,
                                       "help_text": None
                                       }
                                      ],
            "text_attribute_definitions": [{"name": "text_att_test"}],
            "tags": ["new_tag3", "new_tag4"]
        }
        number_resource_group_before = ResourceGroup.objects.all().count()
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(number_resource_group_before,
                         ResourceGroup.objects.all().count())

    def test_create_resource_group_same_tag(self):
        number_tag_before = Tag.objects.all().count()
        data = {
            "name": "new-resource-group-test",
            "attribute_definitions": [],
            "text_attribute_definitions": [],
            "tags": ["new_tag_name1", "new_tag_name2"]
        }
        self._check_resource_created(data=data)
        self.assertEqual(number_tag_before + 2,
                         Tag.objects.all().count())
        data = {
            "name": "new-resource-group-test-2",
            "attribute_definitions": [],
            "text_attribute_definitions": [],
            "tags": ["new_tag_name1", "new_tag_name3"]
        }
        self._check_resource_created(data=data)
        self.assertEqual(number_tag_before + 3,
                         Tag.objects.all().count())
