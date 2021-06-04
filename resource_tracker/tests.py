from django.test import TestCase

from resource_tracker.models import ResourceGroup, ResourceGroupAttributeDefinition, Resource, ResourceAttribute, \
    ResourcePool


class TestCalculation(TestCase):

    def test_ResourceGroup(self):
        name = r'serverGroup1'
        server_group = ResourceGroup.objects.create(name=name)
        self.assertIsInstance(server_group, ResourceGroup)
        self.assertEqual(name, server_group.name)

        attribute = r'CPU'
        server_group.add_attribute_definition(name=attribute)
        self.assertEqual(attribute, server_group.attributes_definition.get(name=attribute).name)
        self.assertIsInstance(server_group.attributes_definition.get(name=attribute), ResourceGroupAttributeDefinition)

    def test_ResourceGroupAddSameAttribute(self):
        server_group = ResourceGroup.objects.create(name="serverGroup1")
        server_group.add_attribute_definition(name='CPU')
        server_group.add_attribute_definition(name='CPU')
        server_group.add_attribute_definition(name='CPU')
        self.assertEqual(1, server_group.attributes_definition.count())
        server_group.add_attribute_definition(name='RAM')
        self.assertEqual(2, server_group.attributes_definition.count())

    def _create_vcenter_pool_with_one_server(self):
        self.server_group = ResourceGroup.objects.create(name="vcenter-pool")
        self.server_group.add_attribute_definition(name='CPU')
        self.server_group.add_attribute_definition(name='RAM')
        self.server1 = self.server_group.create_resource(name="server1")

    def test_create_resource_from_ResourceGroup(self):
        self._create_vcenter_pool_with_one_server()

        self.assertIsInstance(self.server1, Resource)
        self.assertEqual(1, self.server_group.resources.count())

        self.assertIsInstance(self.server1.attributes.get(name='CPU'), ResourceAttribute)
        self.assertEqual('CPU', self.server1.attributes.get(name='CPU').name)
        self.assertEqual(0, self.server1.attributes.get(name='CPU').value)

        self.assertIsInstance(self.server1.attributes.get(name='RAM'), ResourceAttribute)
        self.assertEqual('RAM', self.server1.attributes.get(name='RAM').name)
        self.assertEqual(0, self.server1.attributes.get(name='RAM').value)

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
        self.server1.set_attribute('CPU', 10)
        self.assertEqual(10, self.server1.attributes.get(name='CPU').value)
        self.server1.set_attribute('RAM', 100)
        self.assertEqual(100, self.server1.attributes.get(name='RAM').value)

        server2 = self.server_group.create_resource(name="server2")
        server2.set_attribute('CPU', 100000)
        self.assertEqual(100000, server2.attributes.get(name='CPU').value)
        server2.set_attribute('RAM', 2)
        self.assertEqual(2, server2.attributes.get(name='RAM').value)

        # test override attributes
        self.server1.set_attribute('CPU', 12)
        self.assertEqual(12, self.server1.attributes.get(name='CPU').value)
        self.server1.set_attribute('RAM', 110)
        self.assertEqual(110, self.server1.attributes.get(name='RAM').value)

    def _create_testing_server_group(self):
        self.server_group = ResourceGroup.objects.create(name="server-group")
        self.server_group.add_attribute_definition(name='CPU')
        self.server_group.add_attribute_definition(name='RAM')
        self.cpu_list = [30, 40, 50, 1000]
        i = 0
        for cpu in self.cpu_list:
            i += 1
            server = self.server_group.create_resource(name=f"server{i}-group1")
            server.set_attribute('CPU', cpu)
            self.assertEqual(cpu, server.attributes.get(name='CPU').value)

    def test_get_attribute_on_ResourceGroup(self):
        self._create_testing_server_group()
        self.assertEqual(len(self.cpu_list), self.server_group.resources.count())
        self.assertEqual(sum(self.cpu_list), self.server_group.get_attribute('CPU'))

    def test_link_ResourceGroupAttributeDefinition_to_a_ResourcePool(self):
        self._create_testing_server_group()
        vcenter_pool = ResourcePool.objects.create(name="vcenter-pool")
        vcenter_pool.add_attribute_definition(name='vCPU')

        # Link
        vcenter_pool.attributes_definition.get(name='vCPU')\
            .add_producers(self.server_group.attributes_definition.get(name='CPU'))

        self.assertEqual(sum(self.cpu_list), vcenter_pool.attributes_definition.get(name='vCPU').get_total_produced())

        server5 = self.server_group.create_resource('server5-group1')
        server5.set_attribute('CPU', 100)
        self.assertEqual(sum(self.cpu_list)+100,
                         vcenter_pool.attributes_definition.get(name='vCPU').get_total_produced())

        openshift_pool = ResourcePool.objects.create(name="OpenShift-Pool")
        openshift_pool.add_attribute_definition(name='vCPU')
        # Transfer server-group1.CPU to openshift_pool
        openshift_pool.attributes_definition.get(name='vCPU')\
            .add_producers(self.server_group.attributes_definition.get(name='CPU'))
        # No more resources in vcenterPool.vCPU
        self.assertEqual(0, vcenter_pool.attributes_definition.get(name='vCPU').get_total_produced())
        # All CPU in openshift.vCPU
        self.assertEqual(sum(self.cpu_list)+100,
                         openshift_pool.attributes_definition.get(name='vCPU').get_total_produced())
