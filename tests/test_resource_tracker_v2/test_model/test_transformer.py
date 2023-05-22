from unittest import mock

from django.core.exceptions import ValidationError
from django.db import IntegrityError

from resource_tracker_v2.models import Transformer, ResourceGroup, AttributeDefinition
from resource_tracker_v2.models.resource import Resource
from tests.test_resource_tracker_v2.base_test_resource_tracker_v2 import BaseTestResourceTrackerV2


class TestModelTransformer(BaseTestResourceTrackerV2):

    def setUp(self) -> None:
        super(TestModelTransformer, self).setUp()

    def test_calculate_total_produced(self):
        self.assertEqual(40, self.core_transformer.calculate_total_produced())
        self.assertEqual(20, self.vcpu_from_core_transformer.calculate_total_produced())

    def test_calculate_total_consumed(self):
        self.assertEqual(20, self.core_transformer.calculate_total_consumed())

    def test_get_percent_consumed(self):
        self.core_transformer.refresh_from_db()
        self.assertEqual(50, self.core_transformer.percent_consumed)

    def test_get_available(self):
        self.core_transformer.refresh_from_db()
        self.assertEqual(20, self.core_transformer.available)

    def test_cannot_create_same_transformer_twice(self):
        with self.assertRaises(IntegrityError):
            Transformer.objects.create(resource_group=self.single_vms,
                                       attribute_definition=self.vcpu_attribute,
                                       consume_from_resource_group=self.cluster,
                                       consume_from_attribute_definition=self.core_attribute)

    def test_calculate_total_consumed_with_factor(self):
        self.vcpu_from_core_transformer.refresh_from_db()
        self.vcpu_from_core_transformer.set_factor(4)
        self.core_transformer.refresh_from_db()
        self.assertEqual(5, self.core_transformer.total_consumed)
        self.assertEqual(35, self.core_transformer.available)

    def test_total_consumed_updated_after_resource_deletion(self):
        self.core_transformer.refresh_from_db()
        self.vcpu_from_core_transformer.refresh_from_db()
        self.assertEqual(20, self.vcpu_from_core_transformer.total_produced)
        self.assertEqual(20, self.core_transformer.total_consumed)
        self.vm2.delete()
        self.core_transformer.refresh_from_db()
        self.vcpu_from_core_transformer.refresh_from_db()
        self.assertEqual(5, self.core_transformer.total_consumed)
        self.assertEqual(5, self.vcpu_from_core_transformer.total_produced)

    def test_total_consumed_updated_after_resource_creation(self):
        self.core_transformer.refresh_from_db()
        self.vcpu_from_core_transformer.refresh_from_db()
        self.assertEqual(20, self.core_transformer.total_consumed)
        self.assertEqual(20, self.vcpu_from_core_transformer.total_produced)
        vm3 = Resource.objects.create(name="vm3", resource_group=self.single_vms)
        vm3.set_attribute(self.vcpu_attribute, 2)
        self.core_transformer.refresh_from_db()
        self.vcpu_from_core_transformer.refresh_from_db()
        self.assertEqual(22, self.core_transformer.total_consumed)
        self.assertEqual(22, self.vcpu_from_core_transformer.total_produced)

    def test_total_consumed_updated_after_resource_update(self):
        self.core_transformer.refresh_from_db()
        self.vcpu_from_core_transformer.refresh_from_db()
        self.assertEqual(20, self.core_transformer.total_consumed)
        self.assertEqual(20, self.vcpu_from_core_transformer.total_produced)

        self.vm2.set_attribute(self.vcpu_attribute, 20)

        self.core_transformer.refresh_from_db()
        self.vcpu_from_core_transformer.refresh_from_db()
        self.assertEqual(25, self.core_transformer.total_consumed)
        self.assertEqual(25, self.vcpu_from_core_transformer.total_produced)

    def test_delete_transformer(self):
        self._validate_state_before_deletion()
        self.vcpu_from_core_transformer.delete()
        self._validate_state_after_deletion()

    def test_no_circular_loop_on_transformer(self):
        with self.assertRaises(ValidationError):
            t1 = Transformer.objects.create(resource_group=self.cluster,
                                       attribute_definition=self.core_attribute,
                                       consume_from_resource_group=self.ocp_projects,
                                       consume_from_attribute_definition=self.request_cpu)
            t1._check_circular_loop()

        rwo_storage = AttributeDefinition.objects.create(name="rwo_storage")
        non_circular_transformer = Transformer.objects.create(resource_group=self.ocp_projects,
                                                              attribute_definition=rwo_storage,
                                                              consume_from_resource_group=self.cluster,
                                                              consume_from_attribute_definition=self.three_par_attribute)
        self.assertTrue(non_circular_transformer._check_circular_loop())

    def test_consumption_updated_if_consume_from_set_after_resource_creation(self):
        # add a new RG
        cluster2 = ResourceGroup.objects.create(name="cluster2")
        cluster_2_core_transformer = Transformer.objects.create(resource_group=cluster2,
                                                                attribute_definition=self.core_attribute)
        server3 = Resource.objects.create(name="server3", resource_group=cluster2)
        server3.set_attribute(self.core_attribute, 10)

        self.core_transformer.refresh_from_db()
        cluster_2_core_transformer.refresh_from_db()
        self.vcpu_from_core_transformer.refresh_from_db()
        # change the pointer of consumer
        self.assertEqual(10, cluster_2_core_transformer.total_produced)
        self.assertEqual(20, self.vcpu_from_core_transformer.total_produced)
        self.assertEqual(20, self.core_transformer.total_consumed)
        self.assertEqual(0, cluster_2_core_transformer.total_consumed)
        self.vcpu_from_core_transformer.change_consumer(resource_group=cluster2, attribute=self.core_attribute)
        cluster_2_core_transformer.refresh_from_db()
        self.core_transformer.refresh_from_db()
        self.assertEqual(0, self.core_transformer.total_consumed)
        self.assertEqual(20, cluster_2_core_transformer.total_consumed)

    def test_consumption_with_multiple_resource_group(self):
        self.core_transformer.refresh_from_db()
        self.assertEqual(20, self.core_transformer.total_consumed)

        # add a new RG
        single_vm2 = ResourceGroup.objects.create(name="single_vm2")
        Transformer.objects.create(resource_group=single_vm2,
                                   attribute_definition=self.vcpu_attribute,
                                   consume_from_resource_group=self.cluster,
                                   consume_from_attribute_definition=self.core_attribute)
        vm3 = Resource.objects.create(name="server3", resource_group=single_vm2)
        vm3.set_attribute(self.vcpu_attribute, 10)
        self.core_transformer.refresh_from_db()
        self.assertEqual(30, self.core_transformer.total_consumed)

    def test_resource_group_cannot_consume_from_itself(self):
        new_attribute = AttributeDefinition.objects.create(name="new_attribute")
        with self.assertRaises(IntegrityError):
            Transformer.objects.create(resource_group=self.cluster,
                                       attribute_definition=new_attribute,
                                       consume_from_resource_group=self.cluster,
                                       consume_from_attribute_definition=self.core_attribute)

    def test_resource_group_cannot_consume_from_itself_on_change_consumer(self):
        with self.assertRaises(IntegrityError):
            self.core_transformer.change_consumer(resource_group=self.cluster, attribute=self.three_par_attribute)

    def test_calculate_total_consume_call_only_on_one_layer_parent(self):
        with mock.patch('resource_tracker_v2.models.transformer.Transformer.calculate_total_consumed') as calculate_total_consumed:
            self.project1.set_attribute(self.request_cpu, 20)
            calculate_total_consumed.assert_called_once()

    def test_setting_consumer_auto_add_factor_to_1(self):
        rwo_storage = AttributeDefinition.objects.create(name="rwo_storage")
        new_transformer = Transformer.objects.create(resource_group=self.ocp_projects,
                                                     attribute_definition=rwo_storage,
                                                     consume_from_resource_group=self.cluster,
                                                     consume_from_attribute_definition=self.three_par_attribute)
        self.assertEqual(1, new_transformer.factor)
