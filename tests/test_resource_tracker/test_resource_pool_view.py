from copy import copy

from django.urls import reverse

from resource_tracker.models import ResourcePool, ResourcePoolAttributeDefinition
from tests.test_resource_tracker.base_test_resource_tracker import BaseTestResourceTracker


class TestResourcePoolViews(BaseTestResourceTracker):

    def setUp(self):
        super(TestResourcePoolViews, self).setUp()

    def test_resource_pool_list(self):
        url = reverse('resource_tracker:resource_pool_list')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertTrue("resource_pools" in response.context)

    def test_cannot_get_resource_pool_list_when_logout(self):
        self.client.logout()
        url = reverse('resource_tracker:resource_pool_list')
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)

    def test_resource_pool_create(self):
        url = reverse('resource_tracker:resource_pool_create')
        data = {
            "name": "new_pool",
        }
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        number_rp_before = ResourcePool.objects.all().count()
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(number_rp_before + 1, ResourcePool.objects.all().count())

    def test_resource_pool_edit(self):
        args = {
            "resource_pool_id": self.rp_vcenter.id,
        }
        url = reverse('resource_tracker:resource_pool_edit', kwargs=args)

        new_name = "new_pool_name"
        data = {
            "name": new_name,
        }
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.rp_vcenter.refresh_from_db()
        self.assertEqual(self.rp_vcenter.name, new_name)

    def test_resource_pool_delete(self):
        id_to_delete = copy(self.tower_server_test.id)
        args = {
            'resource_pool_id': self.rp_vcenter.id,
        }
        url = reverse('resource_tracker:resource_pool_delete', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        response = self.client.post(url)
        self.assertEqual(302, response.status_code)
        self.assertFalse(ResourcePool.objects.filter(id=id_to_delete).exists())

    def test_resource_pool_attribute_create(self):
        args = {
            'resource_pool_id': self.rp_vcenter.id,
        }
        url = reverse('resource_tracker:resource_pool_attribute_create', kwargs=args)

        data = {
            "name": "new_attribute"
        }
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertTrue(self.rp_vcenter.attribute_definitions.get(name='new_attribute'))

    def test_resource_pool_attribute_create_with_over_commitment(self):
        args = {
            'resource_pool_id': self.rp_vcenter.id,
        }
        url = reverse('resource_tracker:resource_pool_attribute_create', kwargs=args)

        data = {
            "name": "new_attribute",
            "over_commitment_producers": 2,
            "over_commitment_consumers": 3,
            "yellow_threshold_percent": 70,
            "red_threshold_percent": 85
        }
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertTrue(self.rp_vcenter.attribute_definitions.get(name='new_attribute'))
        self.assertEqual(self.rp_vcenter.attribute_definitions.get(name='new_attribute').over_commitment_producers, 2)
        self.assertEqual(self.rp_vcenter.attribute_definitions.get(name='new_attribute').over_commitment_consumers, 3)

    def test_resource_pool_attribute_create_default_value_on_over_commitment(self):
        args = {
            'resource_pool_id': self.rp_vcenter.id,
        }
        url = reverse('resource_tracker:resource_pool_attribute_create', kwargs=args)

        data = {
            "name": "new_attribute"
        }
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertTrue(self.rp_vcenter.attribute_definitions.get(name='new_attribute'))
        self.assertEqual(self.rp_vcenter.attribute_definitions.get(name='new_attribute').over_commitment_producers,
                         ResourcePoolAttributeDefinition._meta.get_field('over_commitment_producers').default)
        self.assertEqual(self.rp_vcenter.attribute_definitions.get(name='new_attribute').over_commitment_consumers,
                         ResourcePoolAttributeDefinition._meta.get_field('over_commitment_consumers').default)

    def test_cannot_create_existing_attribute(self):
        args = {
            'resource_pool_id': self.rp_vcenter.id,
        }
        url = reverse('resource_tracker:resource_pool_attribute_create', kwargs=args)

        data = {
            "name": "vCPU"
        }
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
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
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        # before executing we do have resource group attributes that consume or produce
        self.assertIsNotNone(self.rg_ocp_workers_vcpu_attribute.consume_from)
        self.assertIsNotNone(self.rg_physical_servers_cpu_attribute.produce_for)
        self.assertTrue(ResourcePoolAttributeDefinition.objects.filter(name="vCPU").exists())
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        # no more producer and consumer
        self.assertFalse(ResourcePoolAttributeDefinition.objects.filter(name="vCPU").exists())
        self.rg_ocp_workers_vcpu_attribute.refresh_from_db()
        self.rg_physical_servers_cpu_attribute.refresh_from_db()
        self.assertIsNone(self.rg_ocp_workers_vcpu_attribute.consume_from)
        self.assertIsNone(self.rg_physical_servers_cpu_attribute.produce_for)

    def test_resource_pool_attribute_edit_name(self):
        args = {
            'resource_pool_id': self.rp_vcenter.id,
            'attribute_id': self.rp_vcenter_vcpu_attribute.id
        }
        url = reverse('resource_tracker:resource_pool_attribute_edit', kwargs=args)
        data = {
            "name": "new_name"
        }
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.rp_vcenter_vcpu_attribute.refresh_from_db()
        self.assertEqual("new_name", self.rp_vcenter_vcpu_attribute.name)

    def test_resource_pool_attribute_edit_over_commitment(self):
        args = {
            'resource_pool_id': self.rp_vcenter.id,
            'attribute_id': self.rp_vcenter_vcpu_attribute.id
        }
        url = reverse('resource_tracker:resource_pool_attribute_edit', kwargs=args)
        data = {
            "name": self.rp_vcenter_vcpu_attribute.name,
            "over_commitment_producers": 1.2,
            "over_commitment_consumers": 1
        }
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.rp_vcenter_vcpu_attribute.refresh_from_db()
        self.assertEqual(1.2, self.rp_vcenter_vcpu_attribute.over_commitment_producers)
        self.assertEqual(1, self.rp_vcenter_vcpu_attribute.over_commitment_consumers)

        # Send form wihtout ouercommitment to use default value
        data = {
            "name": self.rp_vcenter_vcpu_attribute.name
        }
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.rp_vcenter_vcpu_attribute.refresh_from_db()
        self.assertEqual(self.rp_vcenter_vcpu_attribute.over_commitment_producers,
                         ResourcePoolAttributeDefinition._meta.get_field('over_commitment_producers').default)
        self.assertEqual(self.rp_vcenter_vcpu_attribute.over_commitment_consumers,
                         ResourcePoolAttributeDefinition._meta.get_field('over_commitment_consumers').default)

    def test_resource_pool_attribute_producer_list(self):
        args = {
            'resource_pool_id': self.rp_vcenter.id,
            'attribute_id': self.rp_vcenter_vcpu_attribute.id
        }
        url = reverse('resource_tracker:resource_pool_attribute_producer_list', kwargs=args)

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_cannot_get_resource_pool_attribute_producer_list_when_logout(self):
        self.client.logout()
        args = {
            'resource_pool_id': self.rp_vcenter.id,
            'attribute_id': self.rp_vcenter_vcpu_attribute.id
        }
        url = reverse('resource_tracker:resource_pool_attribute_producer_list', kwargs=args)

        response = self.client.get(url)
        self.assertEqual(302, response.status_code)

    def test_resource_pool_attribute_consumer_list(self):
        args = {
            'resource_pool_id': self.rp_vcenter.id,
            'attribute_id': self.rp_vcenter_vcpu_attribute.id
        }
        url = reverse('resource_tracker:resource_pool_attribute_consumer_list', kwargs=args)

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_cannot_get_resource_pool_attribute_consumer_list_when_logout(self):
        self.client.logout()
        args = {
            'resource_pool_id': self.rp_vcenter.id,
            'attribute_id': self.rp_vcenter_vcpu_attribute.id
        }
        url = reverse('resource_tracker:resource_pool_attribute_consumer_list', kwargs=args)

        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
