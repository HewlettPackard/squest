from copy import copy

from resource_tracker_v2.models import Transformer
from resource_tracker_v2.models.resource import Resource, InvalidAttributeDefinition
from service_catalog.models import Service, Instance, InstanceState
from tests.test_resource_tracker_v2.base_test_resource_tracker_v2 import BaseTestResourceTrackerV2


class TestModelResource(BaseTestResourceTrackerV2):

    def setUp(self) -> None:
        super(TestModelResource, self).setUp()

    def _prepare_service_catalog(self):
        self.service_test = Service.objects.create(name="service-test", description="description-of-service-test")
        self.test_instance = Instance.objects.create(name="test_instance_1",
                                                     service=self.service_test,
                                                     requester=self.standard_user,
                                                     quota_scope=self.test_quota_scope
                                                     )
        self.resource_id_to_delete = copy(self.vm1.id)
        self.vm1.service_catalog_instance = self.test_instance
        self.vm1.save()

    def test_create_resource(self):
        server3 = self.cluster.create_resource(name="server3")
        self.assertIsInstance(server3, Resource)
        # check values have been created by default (core and memory)
        self.assertEqual(0, server3.get_attribute_value(attribute_definition=self.core_attribute))
        self.assertEqual(0, server3.get_attribute_value(attribute_definition=self.memory_attribute))

    def test_resource_deleted_on_instance_deletion(self):
        self._prepare_service_catalog()
        self.single_vms.refresh_from_db()
        # delete the instance
        self.assertTrue(self.single_vms.resources.filter(id=self.resource_id_to_delete).exists())
        self.test_instance.delete()
        self.assertFalse(self.single_vms.resources.filter(id=self.resource_id_to_delete).exists())

    def test_resource_deleted_on_instance_state_deleted(self):
        self._prepare_service_catalog()
        self.assertTrue(self.single_vms.resources.filter(id=self.resource_id_to_delete).exists())
        self.test_instance.state = InstanceState.DELETING
        self.test_instance.save()
        self.test_instance.deleted()
        self.assertFalse(self.single_vms.resources.filter(id=self.resource_id_to_delete).exists())

    def test_set_attribute_on_resource(self):
        self.assertEqual(10, self.server1.get_attribute_value(attribute_definition=self.core_attribute))
        self.assertEqual(50, self.server1.get_attribute_value(attribute_definition=self.memory_attribute))

    def test_override_attribute_value(self):
        self.server1.set_attribute(self.core_attribute, 12)
        self.assertEqual(12, self.server1.get_attribute_value(attribute_definition=self.core_attribute))

    def test_set_attribute_on_invalid_attribute(self):
        server2 = self.cluster.create_resource(name="server2")
        with self.assertRaises(InvalidAttributeDefinition):
            server2.set_attribute(self.vcpu_attribute, 10)

    def test_transformer_consumption_updated_on_resource_delete(self):
        transformer = Transformer.objects.get(attribute_definition=self.core_attribute,
                                              resource_group=self.cluster)
        available_before = transformer.available
        self.server1.delete()
        # check consumption updated
        transformer.refresh_from_db()
        self.assertEqual(transformer.available, available_before - 10)

    def test_consumption_updated_on_delete_resource_linked_to_instance(self):
        self._prepare_service_catalog()

        transformer = Transformer.objects.get(attribute_definition=self.vcpu_attribute,
                                              resource_group=self.single_vms)
        available_before = transformer.available
        self.test_instance.delete()
        # check resource is deleted
        self.assertFalse(Resource.objects.filter(id=self.resource_id_to_delete).exists())

        # check consumption updated
        transformer.refresh_from_db()
        self.assertEqual(transformer.available, available_before - 5)
