from resource_tracker_v2.models import AttributeDefinition, ResourceGroup, Resource, Transformer
from tests.test_service_catalog.base import BaseTest


class BaseTestResourceTrackerV2(BaseTest):

    def setUp(self):
        # layer 1: vcenter
        self.core_attribute = AttributeDefinition.objects.create(name="core")
        self.memory_attribute = AttributeDefinition.objects.create(name="memory")
        self.three_par_attribute = AttributeDefinition.objects.create(name="3PAR")

        self.cluster = ResourceGroup.objects.create(name="cluster")
        # cluster --> core
        self.core_transformer = Transformer.objects.create(resource_group=self.cluster,
                                                           attribute_definition=self.core_attribute)
        # cluster --> memory
        Transformer.objects.create(resource_group=self.cluster,
                                   attribute_definition=self.memory_attribute)
        # cluster --> 3par
        Transformer.objects.create(resource_group=self.cluster,
                                   attribute_definition=self.three_par_attribute)

        self.server1 = Resource.objects.create(name="server1", resource_group=self.cluster)
        self.server1.set_attribute(self.core_attribute, 10)
        self.server1.set_attribute(self.memory_attribute, 50)
        self.server1.set_attribute(self.three_par_attribute, 100)

        self.server2 = Resource.objects.create(name="server2", resource_group=self.cluster)
        self.server2.set_attribute(self.core_attribute, 30)
        self.server2.set_attribute(self.memory_attribute, 10)
        self.server2.set_attribute(self.three_par_attribute, 200)

        # layer 2 VM (workers)
        self.single_vms = ResourceGroup.objects.create(name="single_vms")
        self.vcpu_attribute = AttributeDefinition.objects.create(name="vcpu")
        self.v_memory_attribute = AttributeDefinition.objects.create(name="vmemory")
        # vcpu --> core
        self.vcpu_from_core_transformer = Transformer.objects.create(resource_group=self.single_vms,
                                                                     attribute_definition=self.vcpu_attribute,
                                                                     consume_from_resource_group=self.cluster,
                                                                     consume_from_attribute_definition=self.core_attribute)
        # vvmemory --> memory
        self.v_memory_from_memory_transformer = Transformer.objects.create(resource_group=self.single_vms,
                                                                           attribute_definition=self.v_memory_attribute,
                                                                           consume_from_resource_group=self.cluster,
                                                                           consume_from_attribute_definition=self.memory_attribute)

        # add resources
        self.vm1 = Resource.objects.create(name="vm1", resource_group=self.single_vms)
        self.vm1.set_attribute(self.vcpu_attribute, 5)
        self.vm1.set_attribute(self.v_memory_attribute, 4)
        self.vm2 = Resource.objects.create(name="vm2", resource_group=self.single_vms)
        self.vm2.set_attribute(self.vcpu_attribute, 15)
        self.vm2.set_attribute(self.v_memory_attribute, 8)

        # layer 3: ocp project
        self.ocp_projects = ResourceGroup.objects.create(name="ocp_projects")
        self.request_cpu = AttributeDefinition.objects.create(name="request.cpu")
        self.request_memory = AttributeDefinition.objects.create(name="request.memory")
        # request.cpu --> vcpu
        self.request_cpu_from_vcpu = Transformer.objects.create(resource_group=self.ocp_projects,
                                                                attribute_definition=self.request_cpu,
                                                                consume_from_resource_group=self.single_vms,
                                                                consume_from_attribute_definition=self.vcpu_attribute)
        # request.memory --> v-memory
        Transformer.objects.create(resource_group=self.ocp_projects,
                                   attribute_definition=self.request_memory,
                                   consume_from_resource_group=self.single_vms,
                                   consume_from_attribute_definition=self.v_memory_attribute)
        self.project1 = Resource.objects.create(name="project1", resource_group=self.ocp_projects)
        self.project1.set_attribute(self.request_cpu, 10)
        self.project1.set_attribute(self.request_memory, 10)

    def _validate_state_before_deletion(self):
        self.core_transformer.refresh_from_db()
        self.number_attribute_in_vm_before = self.vm1.resource_attributes.count()
        self.assertIsNotNone(self.request_cpu_from_vcpu.consume_from_attribute_definition)
        self.assertIsNotNone(self.request_cpu_from_vcpu.consume_from_resource_group)
        self.parent_consumption_before = self.core_transformer.total_consumed
        self.current_production = self.vcpu_from_core_transformer.total_produced

    def _validate_state_after_deletion(self):
        # assert attribute deleted
        self.vm1.refresh_from_db()
        self.assertEqual(self.number_attribute_in_vm_before - 1, self.vm1.resource_attributes.count())

        # assert children transformer updated
        self.request_cpu_from_vcpu.refresh_from_db()
        self.assertIsNone(self.request_cpu_from_vcpu.consume_from_attribute_definition)
        self.assertIsNone(self.request_cpu_from_vcpu.consume_from_resource_group)

        # assert parent consumption updated
        self.core_transformer.refresh_from_db()
        self.assertEqual(self.parent_consumption_before - self.current_production, self.core_transformer.total_consumed)
