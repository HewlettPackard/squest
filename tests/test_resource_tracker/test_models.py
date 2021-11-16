from random import randint

from django.test import TestCase

from resource_tracker.models import ResourceGroup, ResourceGroupAttributeDefinition, Resource, ResourceAttribute, \
    ResourcePool, ExceptionResourceTracker, ResourceGroupTextAttributeDefinition
from tests.utils import skip_auto_calculation


class TestCalculation(TestCase):

    @skip_auto_calculation
    def _create_simple_testing_stack(self):
        # create a group of server that produce into the vcenter pool
        self.server_group = ResourceGroup.objects.create(name="server-group")
        server_cpu_attribute_def = self.server_group.add_attribute_definition(name='CPU')
        self.server = self.server_group.create_resource(name=f"server-group1")
        self.server.set_attribute(server_cpu_attribute_def, 100)
        self.server_group.calculate_total_resource_of_attributes()
        # create a big server group
        self.big_server_group = ResourceGroup.objects.create(name="big-server-group")
        self.big_server_group_cpu = self.big_server_group.add_attribute_definition(name='CPU')
        self.big_server_group_desc = self.big_server_group.add_text_attribute_definition(name='Description')
        self.big_server_group_cpu_count = 0
        for i in range(5):
            resource = self.big_server_group.create_resource(name=f"big-server-group{i}")
            value = randint(10, 150)
            resource.set_attribute(self.big_server_group_cpu, value)
            self.big_server_group_cpu_count += value
        self.big_server_group.calculate_total_resource_of_attributes()

        self.vcenter_pool = ResourcePool.objects.create(name="vcenter-pool")
        self.vcenter_pool.add_attribute_definition(name='vCPU')
        self.vcenter_pool.attribute_definitions.get(name='vCPU') \
            .add_producers(self.server_group.attribute_definitions.get(name='CPU'))
        self.assertEqual(100, self.vcenter_pool.attribute_definitions.get(name='vCPU').total_produced)
        self.assertIn(member=self.server_group.attribute_definitions.get(name="CPU"),
                      container=self.vcenter_pool.attribute_definitions.get(name='vCPU').producers.all())
        # create VM group that consume
        self.vm_group = ResourceGroup.objects.create(name="vm-group")
        vm_vcpu_attribute = self.vm_group.add_attribute_definition(name='vCPU')
        self.vcenter_pool.attribute_definitions.get(name='vCPU') \
            .add_consumers(self.vm_group.attribute_definitions.get(name='vCPU'))
        self.assertIn(member=self.vm_group.attribute_definitions.get(name='vCPU'),
                      container=self.vcenter_pool.attribute_definitions.get(name='vCPU').consumers.all())
        self.vm1 = self.vm_group.create_resource(name=f"vm1")
        self.vm1.set_attribute(vm_vcpu_attribute, 25)
        vm2 = self.vm_group.create_resource(name=f"vm2")
        vm2.set_attribute(vm_vcpu_attribute, 25)
        self.vm_group.calculate_total_resource_of_attributes()
        self.assertEqual(50, self.vcenter_pool.attribute_definitions.get(name='vCPU').total_consumed)

    def _create_vcenter_pool_with_one_server(self):
        self.server_group = ResourceGroup.objects.create(name="vcenter-pool")
        self.cpu_attribute = self.server_group.add_attribute_definition(name='CPU')
        self.ram_attribute = self.server_group.add_attribute_definition(name='RAM')
        self.server1 = self.server_group.create_resource(name="server1")

    def test_resource_group(self):
        name = r'serverGroup1'
        server_group = ResourceGroup.objects.create(name=name)
        self.assertIsInstance(server_group, ResourceGroup)
        self.assertEqual(name, server_group.name)

        attribute = r'CPU'
        server_group.add_attribute_definition(name=attribute)
        self.assertEqual(attribute, server_group.attribute_definitions.get(name=attribute).name)
        self.assertIsInstance(server_group.attribute_definitions.get(name=attribute), ResourceGroupAttributeDefinition)

    def test_resource_group_add_same_attribute(self):
        server_group = ResourceGroup.objects.create(name="serverGroup1")
        server_group.add_attribute_definition(name='CPU')
        self.assertRaises(ExceptionResourceTracker.AttributeAlreadyExist,
                          server_group.raise_if_attribute_name_exist, 'CPU')
        self.assertRaises(ExceptionResourceTracker.AttributeAlreadyExist, server_group.add_attribute_definition, 'CPU')
        self.assertEqual(1, server_group.attribute_definitions.count())
        server_group.add_attribute_definition(name='RAM')
        self.assertEqual(2, server_group.attribute_definitions.count())

    def test_create_resource_from_resource_group(self):
        self._create_vcenter_pool_with_one_server()

        self.assertIsInstance(self.server1, Resource)
        self.assertEqual(1, self.server_group.resources.count())

        self.assertIsInstance(
            self.server1.attributes.get(attribute_type=ResourceGroupAttributeDefinition.objects.get(name='CPU')),
            ResourceAttribute)
        self.assertEqual(0, self.server1.attributes.get(
            attribute_type=ResourceGroupAttributeDefinition.objects.get(name='CPU')).value)

        self.assertIsInstance(
            self.server1.attributes.get(attribute_type=ResourceGroupAttributeDefinition.objects.get(name='RAM')),
            ResourceAttribute)
        self.assertEqual(0, self.server1.attributes.get(
            attribute_type=ResourceGroupAttributeDefinition.objects.get(name='RAM')).value)

    def test_create_multiple_resource_from_resource_group(self):
        self._create_vcenter_pool_with_one_server()
        server2 = self.server_group.create_resource(name="server2")
        self.assertIsInstance(server2, Resource)
        self.assertEqual(2, self.server_group.resources.count())

        server2 = self.server_group.create_resource(name="server2")
        self.assertIsInstance(server2, Resource)
        self.assertEqual(2, self.server_group.resources.count())

    def test_set_attribute_on_Resource(self):
        self._create_vcenter_pool_with_one_server()
        self.server1.set_attribute(self.cpu_attribute, 10)
        self.assertEqual(10, self.server1.attributes.get(attribute_type=self.cpu_attribute).value)
        self.server1.set_attribute(self.ram_attribute, 100)
        self.assertEqual(100, self.server1.attributes.get(attribute_type=self.ram_attribute).value)

        server2 = self.server_group.create_resource(name="server2")
        server2.set_attribute(self.cpu_attribute, 100000)
        self.assertEqual(100000, server2.attributes.get(attribute_type=self.cpu_attribute).value)
        server2.set_attribute(self.ram_attribute, 2)
        self.assertEqual(2, server2.attributes.get(attribute_type=self.ram_attribute).value)

        # test override attributes
        self.server1.set_attribute(self.cpu_attribute, 12)
        self.assertEqual(12, self.server1.attributes.get(attribute_type=self.cpu_attribute).value)
        self.server1.set_attribute(self.ram_attribute, 110)
        self.assertEqual(110, self.server1.attributes.get(attribute_type=self.ram_attribute).value)

    def _create_testing_server_group(self):
        self.server_group = ResourceGroup.objects.create(name="server-group")
        self.cpu_attribute = self.server_group.add_attribute_definition(name='CPU')
        self.ram_attribute = self.server_group.add_attribute_definition(name='RAM')
        self.cpu_list = [30, 40, 50, 1000]
        i = 0
        for cpu in self.cpu_list:
            i += 1
            server = self.server_group.create_resource(name=f"server{i}-group1")
            server.set_attribute(self.cpu_attribute, cpu)
            self.assertEqual(cpu, server.attributes.get(attribute_type=self.cpu_attribute).value)

    def test_get_attribute_on_resource_group(self):
        self._create_testing_server_group()
        self.assertEqual(len(self.cpu_list), self.server_group.resources.count())
        self.assertEqual(sum(self.cpu_list), self.server_group.get_sum_value_by_attribute(self.cpu_attribute))

    def test_link_resource_group_attribute_definition_to_a_resource_pool(self):
        self._create_testing_server_group()
        vcenter_pool = ResourcePool.objects.create(name="vcenter-pool")
        vcenter_cpu_attribute = vcenter_pool.add_attribute_definition(name='vCPU')

        # Link
        vcenter_pool.attribute_definitions.get(name='vCPU') \
            .add_producers(self.server_group.attribute_definitions.get(name='CPU'))

        self.assertEqual(sum(self.cpu_list), vcenter_pool.attribute_definitions.get(name='vCPU').total_produced)

        server5 = self.server_group.create_resource('server5-group1')
        server5.set_attribute(self.cpu_attribute, 100)
        self.assertEqual(sum(self.cpu_list) + 100,
                         vcenter_pool.attribute_definitions.get(name='vCPU').total_produced)

        openshift_pool = ResourcePool.objects.create(name="OpenShift-Pool")
        ocp_vcpu_attribute = openshift_pool.add_attribute_definition(name='vCPU')
        # Transfer server-group1.CPU to openshift_pool
        openshift_pool.attribute_definitions.get(name='vCPU') \
            .add_producers(self.server_group.attribute_definitions.get(name='CPU'))
        # No more resources in vcenterPool.vCPU
        self.assertEqual(0, vcenter_pool.attribute_definitions.get(name='vCPU').total_produced)
        # All CPU in openshift.vCPU
        self.assertEqual(sum(self.cpu_list) + 100,
                         openshift_pool.attribute_definitions.get(name='vCPU').total_produced)

    def test_get_percent_consumed(self):
        self._create_simple_testing_stack()
        self.assertEqual(50, self.vcenter_pool.attribute_definitions.get(name='vCPU').get_percent_consumed())

    def test_get_total_produced_by(self):
        self._create_simple_testing_stack()
        # add another producer into the vcenter pool
        server_group_2 = ResourceGroup.objects.create(name="server-group-2")
        server_group2_cpu_attribute = server_group_2.add_attribute_definition(name='CPU')
        self.vcenter_pool.attribute_definitions.get(name='vCPU') \
            .add_producers(server_group_2.attribute_definitions.get(name='CPU'))
        server = server_group_2.create_resource(name=f"server-group2")
        server.set_attribute(server_group2_cpu_attribute, 150)

        self.assertEqual(250,
                         self.vcenter_pool.attribute_definitions.get(name='vCPU').total_produced)

        self.assertEqual(100,
                         self.vcenter_pool.attribute_definitions.get(name='vCPU').
                         get_total_produced_by(self.server_group.attribute_definitions.get(name="CPU")))
        self.assertEqual(150,
                         self.vcenter_pool.attribute_definitions.get(name='vCPU').
                         get_total_produced_by(server_group_2.attribute_definitions.get(name="CPU")))

    def test_get_total_consumed_by(self):
        self._create_simple_testing_stack()
        self.assertEqual(50,
                         self.vcenter_pool.attribute_definitions.get(name='vCPU').total_consumed)

        self.assertEqual(50,
                         self.vcenter_pool.attribute_definitions.get(name='vCPU').
                         get_total_consumed_by(self.vm_group.attribute_definitions.get(name="vCPU")))

    def test_get_total_produced_by_with_over_commitment(self):
        self._create_simple_testing_stack()
        # add another producer into the vcenter pool
        server_group_2 = ResourceGroup.objects.create(name="server-group-2")
        server_group2_cpu_attribute = server_group_2.add_attribute_definition(name='CPU')
        self.vcenter_pool.attribute_definitions.get(name='vCPU') \
            .add_producers(server_group_2.attribute_definitions.get(name='CPU'))
        vcpu = self.vcenter_pool.attribute_definitions.get(name='vCPU')
        vcpu.over_commitment_producers = 2
        vcpu.save()
        server = server_group_2.create_resource(name=f"server-group2")
        server.set_attribute(server_group2_cpu_attribute, 150)

        self.assertEqual(500,
                         self.vcenter_pool.attribute_definitions.get(name='vCPU').total_produced)

        self.assertEqual(200,
                         self.vcenter_pool.attribute_definitions.get(name='vCPU').
                         get_total_produced_by(self.server_group.attribute_definitions.get(name="CPU")))
        self.assertEqual(300,
                         self.vcenter_pool.attribute_definitions.get(name='vCPU').
                         get_total_produced_by(server_group_2.attribute_definitions.get(name="CPU")))

    def test_get_total_consumed_by_with_over_commitment(self):
        self._create_simple_testing_stack()
        vcpu = self.vcenter_pool.attribute_definitions.get(name='vCPU')
        vcpu.over_commitment_consumers = 3
        vcpu.save()
        self.assertEqual(150,
                         self.vcenter_pool.attribute_definitions.get(name='vCPU').total_consumed)

        self.assertEqual(150,
                         self.vcenter_pool.attribute_definitions.get(name='vCPU').
                         get_total_consumed_by(self.vm_group.attribute_definitions.get(name="vCPU")))

    def test_edit_resource_group_doesnt_reset_all_resource_values(self):
        self._create_simple_testing_stack()

        rg = ResourceGroup.objects.create(name="My Resource Group")
        cpu = rg.add_attribute_definition("CPU")
        memory = rg.add_attribute_definition("Memory")
        resource = rg.create_resource(f"server-1")
        self.assertEqual(resource.attributes.get(attribute_type=cpu).value, 0)
        self.assertEqual(resource.attributes.get(attribute_type=memory).value, 0)
        resource.attributes.get(attribute_type=cpu).value = 10
        resource.set_attribute(attribute_type=cpu, value=10)
        self.assertEqual(resource.attributes.get(attribute_type=cpu).value, 10)
        rg.edit_attribute_definition(attribute_id=cpu.id, name="CPU")
        self.assertEqual(resource.attributes.get(attribute_type=cpu).value, 10)

    def test_get_total_resource(self):
        self._create_simple_testing_stack()
        self.big_server_group_cpu.refresh_from_db()
        self.assertEqual(self.big_server_group_cpu.total_resource, self.big_server_group_cpu_count)

    def test_edit_text_attribute(self):
        self._create_simple_testing_stack()
        new_name = "New text"
        new_help_text = "help"
        self.big_server_group_desc.edit(new_name, new_help_text)
        self.big_server_group_desc.refresh_from_db()
        self.assertEqual(new_name, self.big_server_group_desc.name)

    def test_edit_attribute(self):
        self._create_simple_testing_stack()
        new_name = "Memory"
        new_help_text = "help"
        new_produce_for = self.vcenter_pool.attribute_definitions.get(name='vCPU')
        new_consume_from = None
        self.big_server_group_cpu.edit(new_name, new_produce_for, new_consume_from, new_help_text)
        self.big_server_group_cpu.refresh_from_db()
        self.assertEqual(new_name, self.big_server_group_cpu.name)
        self.assertEqual(new_consume_from, self.big_server_group_cpu.consume_from)
        self.assertEqual(new_produce_for, self.big_server_group_cpu.produce_for)

    def test_add_new_text_attribute(self):
        # add + init methods
        self._create_simple_testing_stack()
        self.big_server_group.add_text_attribute_definition('New text attribute')
        self.big_server_group.refresh_from_db()
        for resource in self.big_server_group.resources.all():
            attribute_type = ResourceGroupTextAttributeDefinition.objects.get(name='New text attribute')
            attribute = resource.text_attributes.get(text_attribute_type=attribute_type)
            self.assertEqual(attribute.value, "")

    def test_add_new_attribute(self):
        # add + init methods
        self._create_simple_testing_stack()
        self.big_server_group.add_attribute_definition('New attribute')
        self.big_server_group.refresh_from_db()
        for resource in self.big_server_group.resources.all():
            attribute_type = ResourceGroupAttributeDefinition.objects.get(name='New attribute')
            attribute = resource.attributes.get(attribute_type=attribute_type)
            self.assertEqual(attribute.value, 0)

    def test_help_text_on_attribute_definition(self):
        rg = ResourceGroup.objects.create(name="My Resource Group")
        cpu = rg.add_attribute_definition("CPU", help_text="HEELP")
        self.assertEqual(cpu.help_text, "HEELP")

    def test_help_text_on_text_attribute_definition(self):
        rg = ResourceGroup.objects.create(name="My Resource Group")
        cpu = rg.add_text_attribute_definition("CPU", help_text="HEELP")
        self.assertEqual(cpu.help_text, "HEELP")

    def test_remove_all_producer(self):
        self._create_simple_testing_stack()
        self.vcenter_pool.attribute_definitions.get(name='vCPU').remove_all_producer()
        self.assertEqual(self.vcenter_pool.attribute_definitions.get(name='vCPU').producers.count(), 0)

    def test_remove_all_consumer(self):
        self._create_simple_testing_stack()
        self.vcenter_pool.attribute_definitions.get(name='vCPU').remove_all_consumer()
        self.assertEqual(self.vcenter_pool.attribute_definitions.get(name='vCPU').consumers.count(), 0)

    def test_delete_resource_group_also_delete_resource(self):
        self._create_simple_testing_stack()
        self.assertTrue(Resource.objects.filter(id=self.server.id).exists())
        self.server_group.delete()
        self.assertFalse(Resource.objects.filter(id=self.server.id).exists())

    def test_resource_update_after_delete_resource(self):
        self._create_simple_testing_stack()
        self.assertEqual(50, self.vcenter_pool.attribute_definitions.get(name='vCPU').total_consumed)
        self.vm1.delete()
        self.assertEqual(25, self.vcenter_pool.attribute_definitions.get(name='vCPU').total_consumed)

    def test_pool_updated_after_adding_consumer_on_attribute(self):
        # initial. A RP anf RG with one resource. No link yet
        vcenter_pool = ResourcePool.objects.create(name="vcenter-pool")
        vcenter_pool_vcpu_att = vcenter_pool.add_attribute_definition(name='vCPU')
        server_group = ResourceGroup.objects.create(name="server-group")
        server_cpu_attribute_def = server_group.add_attribute_definition(name='CPU')
        server = server_group.create_resource(name=f"server-group1")
        server.set_attribute(server_cpu_attribute_def, 100)
        self.assertEqual(0, vcenter_pool_vcpu_att.total_produced)

        # add link
        vcenter_pool.attribute_definitions.get(name='vCPU') \
            .add_producers(server_group.attribute_definitions.get(name='CPU'))

        # assert pool consumption is updated
        vcenter_pool_vcpu_att.refresh_from_db()
        self.assertEqual(100, vcenter_pool_vcpu_att.total_produced)

    def test_pool_updated_after_deleting_consumer_on_attribute(self):
        # initial. A RP anf RG with one resource
        vcenter_pool = ResourcePool.objects.create(name="vcenter-pool")
        vcenter_pool_vcpu_att = vcenter_pool.add_attribute_definition(name='vCPU')
        server_group = ResourceGroup.objects.create(name="server-group")
        server_cpu_attribute_def = server_group.add_attribute_definition(name='CPU')
        server = server_group.create_resource(name=f"server-group1")
        server.set_attribute(server_cpu_attribute_def, 100)
        vcenter_pool.attribute_definitions.get(name='vCPU') \
            .add_producers(server_group.attribute_definitions.get(name='CPU'))
        vcenter_pool_vcpu_att.refresh_from_db()
        self.assertEqual(100, vcenter_pool_vcpu_att.total_produced)

        # delete RP
        server_group.delete()
        vcenter_pool_vcpu_att.refresh_from_db()
        self.assertEqual(0, vcenter_pool_vcpu_att.total_produced)
