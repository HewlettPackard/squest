from copy import copy

from django.urls import reverse

from resource_tracker.models import ResourcePool, ResourcePoolAttributeDefinition
from resource_tracker.tests.base_test_resource_tracker import BaseTestResourceTracker


class TestResourcePoolViews(BaseTestResourceTracker):

    def setUp(self):
        super(TestResourcePoolViews, self).setUp()

    def test_resource_pool_list(self):
        url = reverse('resource_tracker:resource_pool_list')
        response = self.client.get(url)
        self.assertEquals(200, response.status_code)
        self.assertTrue("resource_pools" in response.context)
        self.assertTrue("list_attribute_name" in response.context)

    def test_resource_pool_create(self):
        url = reverse('resource_tracker:resource_pool_create')
        data = {
            "name": "new_pool",
        }
        number_rp_before = ResourcePool.objects.all().count()
        response = self.client.post(url, data=data)
        self.assertEquals(302, response.status_code)
        self.assertEquals(number_rp_before + 1, ResourcePool.objects.all().count())

    def test_resource_pool_edit(self):
        args = {
            "resource_pool_id": self.rp_vcenter.id,
        }
        url = reverse('resource_tracker:resource_pool_edit', kwargs=args)

        new_name = "new_pool_name"
        data = {
            "name": new_name,
        }
        response = self.client.post(url, data=data)
        self.assertEquals(302, response.status_code)
        self.rp_vcenter.refresh_from_db()
        self.assertEquals(self.rp_vcenter.name, new_name)

    def test_resource_pool_delete(self):
        id_to_delete = copy(self.tower_server_test.id)
        args = {
            'resource_pool_id': self.rp_vcenter.id,
        }
        url = reverse('resource_tracker:resource_pool_delete', kwargs=args)
        response = self.client.post(url)
        self.assertEquals(302, response.status_code)
        self.assertFalse(ResourcePool.objects.filter(id=id_to_delete).exists())

    def test_resource_pool_attribute_create(self):
        args = {
            'resource_pool_id': self.rp_vcenter.id,
        }
        url = reverse('resource_tracker:resource_pool_attribute_create', kwargs=args)

        data = {
            "name": "new_attribute"
        }
        response = self.client.post(url, data=data)
        self.assertEquals(302, response.status_code)
        self.assertTrue(self.rp_vcenter.attributes_definition.get(name='new_attribute'))

    def test_cannot_create_existing_attribute(self):
        args = {
            'resource_pool_id': self.rp_vcenter.id,
        }
        url = reverse('resource_tracker:resource_pool_attribute_create', kwargs=args)

        data = {
            "name": "vCPU"
        }
        response = self.client.post(url, data=data)
        self.assertEquals(200, response.status_code)
        self.assertContains(response, 'Attribute with this name already exists for this resource pool')

    def test_resource_pool_attribute_delete(self):
        args = {
            'resource_pool_id': self.rp_vcenter.id,
            'attribute_id': self.rp_vcenter_vcpu_attribute.id
        }
        url = reverse('resource_tracker:resource_pool_attribute_delete', kwargs=args)

        data = {
            "name": "vCPU"
        }
        # before executing we do have resource group attributes that consume or produce
        self.assertIsNotNone(self.rg_ocp_workers_vcpu_attribute.consume_from)
        self.assertIsNotNone(self.rg_physical_servers_cpu_attribute.produce_for)
        self.assertTrue(ResourcePoolAttributeDefinition.objects.filter(name="vCPU").exists())
        response = self.client.post(url, data=data)
        self.assertEquals(302, response.status_code)
        # no more producer and consumer
        self.assertFalse(ResourcePoolAttributeDefinition.objects.filter(name="vCPU").exists())
        self.rg_ocp_workers_vcpu_attribute.refresh_from_db()
        self.rg_physical_servers_cpu_attribute.refresh_from_db()
        self.assertIsNone(self.rg_ocp_workers_vcpu_attribute.consume_from)
        self.assertIsNone(self.rg_physical_servers_cpu_attribute.produce_for)

    def test_resource_pool_attribute_edit(self):
        args = {
            'resource_pool_id': self.rp_vcenter.id,
            'attribute_id': self.rp_vcenter_vcpu_attribute.id
        }
        url = reverse('resource_tracker:resource_pool_attribute_edit', kwargs=args)
        data = {
            "name": "new_name"
        }
        response = self.client.post(url, data=data)
        self.assertEquals(302, response.status_code)
        self.rp_vcenter_vcpu_attribute.refresh_from_db()
        self.assertEquals("new_name", self.rp_vcenter_vcpu_attribute.name)

    def test_resource_pool_attribute_producer_list(self):
        args = {
            'resource_pool_id': self.rp_vcenter.id,
            'attribute_id': self.rp_vcenter_vcpu_attribute.id
        }
        url = reverse('resource_tracker:resource_pool_attribute_producer_list', kwargs=args)

        response = self.client.get(url)
        self.assertEquals(200, response.status_code)

    def test_resource_pool_attribute_consumer_list(self):
        args = {
            'resource_pool_id': self.rp_vcenter.id,
            'attribute_id': self.rp_vcenter_vcpu_attribute.id
        }
        url = reverse('resource_tracker:resource_pool_attribute_consumer_list', kwargs=args)

        response = self.client.get(url)
        self.assertEquals(200, response.status_code)
