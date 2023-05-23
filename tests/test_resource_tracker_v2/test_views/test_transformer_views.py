from django.urls import reverse

from resource_tracker_v2.models import Transformer
from tests.test_resource_tracker_v2.base_test_resource_tracker_v2 import BaseTestResourceTrackerV2


class TestTransformerViews(BaseTestResourceTrackerV2):

    def setUp(self):
        super(TestTransformerViews, self).setUp()

    def test_get_transformer(self):
        args = {
            "resource_group_id": self.ocp_projects.id
        }

        response = self.client.get(reverse('resource_tracker:resource_group_attribute_list', kwargs=args))
        self.assertEqual(200, response.status_code)

    def test_create_transformer_no_consumer(self):
        args = {
            'resource_group_id': self.ocp_projects.id,
        }
        data = {
            "attribute_definition": self.three_par_attribute.id,
        }
        number_transformer_before = Transformer.objects.all().count()
        response = self.client.post(reverse('resource_tracker:resource_group_attribute_create', kwargs=args),
                                    data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(number_transformer_before + 1, Transformer.objects.all().count())

    def test_create_transformer_with_consumer(self):
        args = {
            "resource_group_id": self.ocp_projects.id,
        }
        data = {
            "attribute_definition": self.three_par_attribute.id,
            "consume_from_resource_group": self.cluster.id,
            "consume_from_attribute_definition": self.three_par_attribute.id,
        }
        number_transformer_before = Transformer.objects.all().count()

        # get
        response = self.client.get(reverse('resource_tracker:resource_group_attribute_create', kwargs=args))
        self.assertEqual(200, response.status_code)

        # post
        response = self.client.post(reverse('resource_tracker:resource_group_attribute_create', kwargs=args),
                                    data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(number_transformer_before + 1, Transformer.objects.all().count())

    def test_edit_transformer(self):
        args = {
            "resource_group_id": self.ocp_projects.id,
            "attribute_id": self.request_cpu.id,
        }
        data = {
            "consume_from_resource_group": self.cluster.id,
            "consume_from_attribute_definition": self.three_par_attribute.id,
            "factor": 10
        }
        self.assertEqual(self.request_cpu_from_vcpu.factor, 1)
        self.assertEqual(self.request_cpu_from_vcpu.consume_from_resource_group.id, self.single_vms.id)
        self.assertEqual(self.request_cpu_from_vcpu.consume_from_attribute_definition.id, self.vcpu_attribute.id)

        # get
        response = self.client.get(reverse('resource_tracker:resource_group_attribute_edit', kwargs=args))
        self.assertEqual(200, response.status_code)

        # post
        response = self.client.post(reverse('resource_tracker:resource_group_attribute_edit', kwargs=args),
                                    data=data)
        self.assertEqual(302, response.status_code)
        self.request_cpu_from_vcpu.refresh_from_db()
        self.assertEqual(self.request_cpu_from_vcpu.factor, 10)
        self.assertEqual(self.request_cpu_from_vcpu.consume_from_resource_group.id, self.cluster.id)
        self.assertEqual(self.request_cpu_from_vcpu.consume_from_attribute_definition.id, self.three_par_attribute.id)

    def test_delete_transformer(self):
        self.assertTrue(self.server1.resource_attributes.filter(attribute_definition=self.core_attribute).exists())
        self.assertTrue(self.server2.resource_attributes.filter(attribute_definition=self.core_attribute).exists())
        args = {
            'resource_group_id': self.cluster.id,
            'attribute_id': self.core_attribute.id,
        }

        # get
        response = self.client.get(reverse('resource_tracker:resource_group_attribute_delete', kwargs=args))
        self.assertEqual(200, response.status_code)

        # post
        response = self.client.post(reverse('resource_tracker:resource_group_attribute_delete', kwargs=args))
        self.assertEqual(302, response.status_code)
        self.server1.refresh_from_db()
        self.server2.refresh_from_db()
        self.assertFalse(self.server1.resource_attributes.filter(attribute_definition=self.core_attribute).exists())
        self.assertFalse(self.server2.resource_attributes.filter(attribute_definition=self.core_attribute).exists())
