from copy import copy

from django.urls import reverse

from resource_tracker.models import ResourcePool, ResourcePoolAttributeDefinition
from tests.test_resource_tracker.base_test_resource_tracker import BaseTestResourceTracker


class TestResourcePoolViews(BaseTestResourceTracker):

    def setUp(self):
        super(TestResourcePoolViews, self).setUp()
        self.rp_test_without_tag = ResourcePool.objects.create(name="without_tag")
        self.rp_test = ResourcePool.objects.create(name="test")
        self.rp_test.tags.add("test1")
        self.rp_test.tags.add("test2")
        self.rp_vcenter.tags.add("test1")
        self.rp_ocp_workers.tags.add("test2")

    def test_resource_pool_list(self):
        url = reverse('resource_tracker:resource_pool_list')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertTrue("resource_pools" in response.context)
        self.assertEqual(response.context['resource_pools'].qs.count(), ResourcePool.objects.count())

    def test_resource_pool_list_filter_type_and(self):
        url = reverse('resource_tracker:resource_pool_list') + "?tag=test1&tag=test2&tag_filter_type=AND"
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.context['resource_pools'].qs.count(), 1)

    def test_resource_pool_list_filter_type_or(self):
        url = reverse('resource_tracker:resource_pool_list') + "?tag=test1&tag=test2&tag_filter_type=OR"
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.context['resource_pools'].qs.count(), 3)
        
    def test_get_resource_pool_with_one_tag_in_session(self):
        url = reverse('resource_tracker:resource_pool_list')

        # try to get all resource pool
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.context["resource_pools"].qs.count(), ResourcePool.objects.all().count())

        # get the page by giving a tag into the URL (like the button apply filter)
        response = self.client.get(url + f"?tag=test1&tag_filter_type=OR")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.context["resource_pools"].qs.count(), 2)

        # move to another page
        response = self.client.get(reverse('service_catalog:doc_list'))
        self.assertEqual(200, response.status_code)

        # go back to the resource loop list without a tag in the URL
        response = self.client.get(url, follow=True)  # follow the redirect
        self.assertEqual(200, response.status_code)
        self.assertIn("test1", response.request["QUERY_STRING"])
        self.assertIn("OR", response.request["QUERY_STRING"])
        self.assertEqual(response.context["resource_pools"].qs.count(), 2)

        # save tags and type
        response = self.client.get(url + f"?tag=test1&tag=test2&tag_filter_type=AND")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.context["resource_pools"].qs.count(), 1)

        # move to another page
        response = self.client.get(reverse('service_catalog:doc_list'))
        self.assertEqual(200, response.status_code)

        # go back to the resource group list without a tag in the URL
        response = self.client.get(url, follow=True)  # follow the redirect
        self.assertEqual(200, response.status_code)
        self.assertIn("test1", response.request["QUERY_STRING"])
        self.assertIn("test2", response.request["QUERY_STRING"])
        self.assertIn("AND", response.request["QUERY_STRING"])
        self.assertEqual(response.context["resource_pools"].qs.count(), 1)

        # save type
        response = self.client.get(url + f"?tag_filter_type=AND")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.context["resource_pools"].qs.count(), ResourcePool.objects.count())

        # move to another page
        response = self.client.get(reverse('service_catalog:doc_list'))
        self.assertEqual(200, response.status_code)

        # go back to the resource group list without a tag in the URL
        response = self.client.get(url, follow=True)  # follow the redirect
        self.assertEqual(200, response.status_code)
        self.assertIn("AND", response.request["QUERY_STRING"])
        self.assertEqual(response.context["resource_pools"].qs.count(), ResourcePool.objects.count())

        # reset tags and type
        response = self.client.get(url + f"?tag_filter_type=OR")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.context["resource_pools"].qs.count(), ResourcePool.objects.count())

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
