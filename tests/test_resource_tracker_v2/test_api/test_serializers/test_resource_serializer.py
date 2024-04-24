from resource_tracker_v2.api.serializers.resource_serializer import ResourceSerializer
from resource_tracker_v2.models import Resource, Transformer
from tests.test_resource_tracker_v2.base_test_resource_tracker_v2 import BaseTestResourceTrackerV2API


class ResourceSerializerTests(BaseTestResourceTrackerV2API):

    def setUp(self):
        super(ResourceSerializerTests, self).setUp()
        self.number_resource_before = Resource.objects.all().count()

    def _validate_created(self):
        self.assertEqual(self.number_resource_before + 1, Resource.objects.all().count())

    def test_create_resource(self):
        transformer = Transformer.objects.get(attribute_definition=self.core_attribute,
                                              resource_group=self.cluster)
        available_before = transformer.available
        core_attribute_value = 10

        data = {
            "resource_group": self.cluster.id,
            "name": "new_server",
            "service_catalog_instance": None,
            "is_deleted_on_instance_deletion": False,
            "resource_attributes": [
                {"name": "core",
                 "value": core_attribute_value
                 }
            ],
        }
        serializer = ResourceSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self._validate_created()

        transformer.refresh_from_db()
        self.assertEqual(transformer.available, available_before + core_attribute_value)

    def test_update_resource(self):
        transformer = Transformer.objects.get(attribute_definition=self.core_attribute,
                                              resource_group=self.cluster)
        available_before = transformer.available
        core_attribute_before = 10
        new_core_attribute_value = 20

        data = {
            "resource_group": self.cluster.id,
            "name": "new_server",
            "service_catalog_instance": None,
            "is_deleted_on_instance_deletion": False,
            "resource_attributes": [
                {"name": "core",
                 "value": new_core_attribute_value
                 }
            ],
        }
        serializer = ResourceSerializer(instance=self.server1, data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        # check consumption updated
        transformer.refresh_from_db()
        self.assertEqual(transformer.available, available_before - core_attribute_before + new_core_attribute_value)
