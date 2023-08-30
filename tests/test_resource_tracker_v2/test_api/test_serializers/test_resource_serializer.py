from resource_tracker_v2.api.serializers.resource_serializer import ResourceSerializer
from resource_tracker_v2.models import Resource
from tests.test_resource_tracker_v2.base_test_resource_tracker_v2 import BaseTestResourceTrackerV2API


class ResourceSerializerTests(BaseTestResourceTrackerV2API):

    def setUp(self):
        super(ResourceSerializerTests, self).setUp()
        self.number_resource_before = Resource.objects.all().count()

    def _validate_created(self):
        self.assertEqual(self.number_resource_before + 1, Resource.objects.all().count())

    def test_create_resource(self):
        data = {
            "resource_group": self.cluster.id,
            "name": "new_server",
            "service_catalog_instance": None,
            "is_deleted_on_instance_deletion": False,
            "resource_attributes": [
                {"name": "core",
                 "value": 10
                 }
            ],
        }
        serializer = ResourceSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self._validate_created()
