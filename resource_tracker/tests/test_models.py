from django.test import TestCase

from resource_tracker.models import ResourceGroup, ResourceGroupAttributeDefinition, Resource, ResourceAttribute, \
    ResourcePool


class TestCalculation(TestCase):

    def _create_simple_testing_stack(self):
        # create a group of server that produce into the vcenter pool
        self.server_group = ResourceGroup.objects.create(name="server-group")
        server_cpu_attribute_def = self.server_group.add_attribute_definition(name='CPU')
        server = self.server_group.create_resource(name=f"server-group1")
        server.set_attribute(server_cpu_attribute_def, 100)

        self.vcenter_pool = ResourcePool.objects.create(name="vcenter-pool")
        self.vcenter_pool.add_attribute_definition(name='vCPU')
        self.vcenter_pool.attributes_definition.get(name='vCPU') \
            .add_producers(self.server_group.attribute_definitions.get(name='CPU'))
        self.assertEqual(100, self.vcenter_pool.attributes_definition.get(name='vCPU').get_total_produced())

        # create VM group that consume
        self.vm_group = ResourceGroup.objects.create(name="vm-group")
        vm_vcpu_attribute = self.vm_group.add_attribute_definition(name='vCPU')
        self.vcenter_pool.attributes_definition.get(name='vCPU') \
            .add_consumers(self.vm_group.attribute_definitions.get(name='vCPU'))
        vm1 = self.vm_group.create_resource(name=f"vm1")
        vm1.set_attribute(vm_vcpu_attribute, 25)
        vm2 = self.vm_group.create_resource(name=f"vm2")
        vm2.set_attribute(vm_vcpu_attribute, 25)
        self.assertEqual(50, self.vcenter_pool.attributes_definition.get(name='vCPU').get_total_consumed())

    def _create_vcenter_pool_with_one_server(self):
        self.server_group = ResourceGroup.objects.create(name="vcenter-pool")
        self.cpu_attribute = self.server_group.add_attribute_definition(name='CPU')
        self.ram_attribute = self.server_group.add_attribute_definition(name='RAM')
        self.server1 = self.server_group.create_resource(name="server1")

    def test_ResourceGroup(self):
        name = r'serverGroup1'
        server_group = ResourceGroup.objects.create(name=name)
        self.assertIsInstance(server_group, ResourceGroup)
        self.assertEqual(name, server_group.name)

        attribute = r'CPU'
        server_group.add_attribute_definition(name=attribute)
        self.assertEqual(attribute, server_group.attribute_definitions.get(name=attribute).name)
        self.assertIsInstance(server_group.attribute_definitions.get(name=attribute), ResourceGroupAttributeDefinition)

    def test_ResourceGroupAddSameAttribute(self):
        server_group = ResourceGroup.objects.create(name="serverGroup1")
        server_group.add_attribute_definition(name='CPU')
        server_group.add_attribute_definition(name='CPU')
        server_group.add_attribute_definition(name='CPU')
        self.assertEqual(1, server_group.attribute_definitions.count())
        server_group.add_attribute_definition(name='RAM')
        self.assertEqual(2, server_group.attribute_definitions.count())

    def test_create_resource_from_ResourceGroup(self):
        self._create_vcenter_pool_with_one_server()

        self.assertIsInstance(self.server1, Resource)
        self.assertEqual(1, self.server_group.resources.count())

        self.assertIsInstance(self.server1.attributes.get(attribute_type=ResourceGroupAttributeDefinition.objects.get(name='CPU')), ResourceAttribute)
        self.assertEqual(0, self.server1.attributes.get(attribute_type=ResourceGroupAttributeDefinition.objects.get(name='CPU')).value)

        self.assertIsInstance(self.server1.attributes.get(attribute_type=ResourceGroupAttributeDefinition.objects.get(name='RAM')), ResourceAttribute)
        self.assertEqual(0, self.server1.attributes.get(attribute_type=ResourceGroupAttributeDefinition.objects.get(name='RAM')).value)

    def test_create_multiple_resource_from_ResourceGroup(self):
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

    def test_get_attribute_on_ResourceGroup(self):
        self._create_testing_server_group()
        self.assertEqual(len(self.cpu_list), self.server_group.resources.count())
        self.assertEqual(sum(self.cpu_list), self.server_group.get_attribute(self.cpu_attribute))

    def test_link_ResourceGroupAttributeDefinition_to_a_ResourcePool(self):
        self._create_testing_server_group()
        vcenter_pool = ResourcePool.objects.create(name="vcenter-pool")
        vcenter_cpu_attribute = vcenter_pool.add_attribute_definition(name='vCPU')

        # Link
        vcenter_pool.attributes_definition.get(name='vCPU') \
            .add_producers(self.server_group.attribute_definitions.get(name='CPU'))

        self.assertEqual(sum(self.cpu_list), vcenter_pool.attributes_definition.get(name='vCPU').get_total_produced())

        server5 = self.server_group.create_resource('server5-group1')
        server5.set_attribute(self.cpu_attribute, 100)
        self.assertEqual(sum(self.cpu_list) + 100,
                         vcenter_pool.attributes_definition.get(name='vCPU').get_total_produced())

        openshift_pool = ResourcePool.objects.create(name="OpenShift-Pool")
        ocp_vcpu_attribute = openshift_pool.add_attribute_definition(name='vCPU')
        # Transfer server-group1.CPU to openshift_pool
        openshift_pool.attributes_definition.get(name='vCPU') \
            .add_producers(self.server_group.attribute_definitions.get(name='CPU'))
        # No more resources in vcenterPool.vCPU
        self.assertEqual(0, vcenter_pool.attributes_definition.get(name='vCPU').get_total_produced())
        # All CPU in openshift.vCPU
        self.assertEqual(sum(self.cpu_list) + 100,
                         openshift_pool.attributes_definition.get(name='vCPU').get_total_produced())

    def test_get_percent_consumed(self):
        self._create_simple_testing_stack()
        self.assertEqual(50, self.vcenter_pool.attributes_definition.get(name='vCPU').get_percent_consumed())

    def test_get_total_produced_by(self):
        self._create_simple_testing_stack()
        # add another producer into the vcenter pool
        server_group_2 = ResourceGroup.objects.create(name="server-group-2")
        server_group2_cpu_attribute = server_group_2.add_attribute_definition(name='CPU')
        self.vcenter_pool.attributes_definition.get(name='vCPU') \
            .add_producers(server_group_2.attribute_definitions.get(name='CPU'))
        server = server_group_2.create_resource(name=f"server-group2")
        server.set_attribute(server_group2_cpu_attribute, 150)

        self.assertEqual(250,
                         self.vcenter_pool.attributes_definition.get(name='vCPU').get_total_produced())

        self.assertEqual(100,
                         self.vcenter_pool.attributes_definition.get(name='vCPU').
                         get_total_produced_by(self.server_group.attribute_definitions.get(name="CPU")))
        self.assertEqual(150,
                         self.vcenter_pool.attributes_definition.get(name='vCPU').
                         get_total_produced_by(server_group_2.attribute_definitions.get(name="CPU")))

    def test_get_total_consumed_by(self):
        self._create_simple_testing_stack()
        self.assertEqual(100,
                         self.vcenter_pool.attributes_definition.get(name='vCPU').get_total_produced())

        self.assertEqual(50,
                         self.vcenter_pool.attributes_definition.get(name='vCPU').
                         get_total_consumed_by(self.vm_group.attribute_definitions.get(name="vCPU")))
