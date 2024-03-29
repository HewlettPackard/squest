from django.db import IntegrityError

from resource_tracker_v2.api.serializers.transformer_serializer import TransformerSerializer
from resource_tracker_v2.models import AttributeDefinition, ResourceGroup, Transformer
from tests.test_resource_tracker_v2.base_test_resource_tracker_v2 import BaseTestResourceTrackerV2API


class TransformerSerializerTests(BaseTestResourceTrackerV2API):

    def setUp(self):
        super(TransformerSerializerTests, self).setUp()
        self.new_rg = ResourceGroup.objects.create(name="new_rg")
        self.new_attribute = AttributeDefinition.objects.create(name="new_attribute")
        self.new_transformer = Transformer.objects.create(resource_group=self.new_rg,
                                                          attribute_definition=self.core_attribute)
        self.data = {
            "resource_group": self.cluster.id
        }
        self.number_transformer_before = Transformer.objects.all().count()

    def _validate_transformer_created(self):
        self.assertEqual(self.number_transformer_before + 1, Transformer.objects.all().count())

    def test_create_transformer_no_consumption(self):
        self.data["attribute_definition"] = self.new_attribute.id
        self.data["consume_from_resource_group"] = None
        self.data["consume_from_attribute_definition"] = None
        serializer = TransformerSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self._validate_transformer_created()

    def test_create_transformer_with_consumption(self):
        self.data["attribute_definition"] = self.new_attribute.id
        self.data["consume_from_resource_group"] = self.new_rg.id
        self.data["consume_from_attribute_definition"] = self.core_attribute.id
        serializer = TransformerSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self._validate_transformer_created()

    def test_cannot_create_transformer_with_target_rg_and_no_target_attribute(self):
        self.data["attribute_definition"] = self.new_attribute.id
        self.data["consume_from_resource_group"] = self.new_rg.id
        self.data["consume_from_attribute_definition"] = None
        serializer = TransformerSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), {'consume_from_attribute_definition'})

    def test_cannot_create_transformer_with_not_target_rg_and_target_attribute(self):
        self.data["attribute_definition"] = self.new_attribute.id
        self.data["consume_from_resource_group"] = None
        self.data["consume_from_attribute_definition"] = self.new_attribute.id
        serializer = TransformerSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), {'consume_from_resource_group'})

    def test_transformer_exist_already_on_selected_attribute(self):
        self.data["attribute_definition"] = self.core_attribute.id
        self.data["consume_from_resource_group"] = None
        self.data["consume_from_attribute_definition"] = None
        serializer = TransformerSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertIn(f"The fields resource_group, attribute_definition must make a unique set.", serializer.errors["non_field_errors"][0])

    def test_invalid_target_attribute_in_transformer(self):
        self.data["attribute_definition"] = self.new_attribute.id
        self.data["consume_from_resource_group"] = self.new_rg.id
        self.data["consume_from_attribute_definition"] = self.vcpu_attribute.id
        serializer = TransformerSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), {'consume_from_attribute'})

    def test_can_link_attribute_to_multiple_same_attribute_def_from_different_rg(self):
        other_vms = ResourceGroup.objects.create(name="other_vms")
        Transformer.objects.create(resource_group=other_vms, attribute_definition=self.vcpu_attribute)
        other_field = AttributeDefinition.objects.create(name="other_field")
        self.data["attribute_definition"] = other_field.id
        self.data["consume_from_resource_group"] = other_vms.id
        self.data["consume_from_attribute_definition"] = self.vcpu_attribute.id
        self.data['resource_group'] = self.single_vms.id
        serializer = TransformerSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        self._validate_transformer_created()

    def test_cannot_create_circular_loop_when_adding_consumer(self):
        self.data["attribute_definition"] = self.core_attribute.id
        self.data["consume_from_resource_group"] = self.ocp_projects.id
        self.data["consume_from_attribute_definition"] = self.request_cpu.id
        serializer = TransformerSerializer(instance=self.core_transformer, data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), {'consume_from_attribute_definition'})

    def test_update_factor_also_update_parent_consumption(self):
        consumption_before = self.core_transformer.total_consumed
        self.data["attribute_definition"] = self.vcpu_attribute.id
        self.data["consume_from_resource_group"] = self.cluster.id
        self.data["consume_from_attribute_definition"] = self.core_attribute.id
        self.data["factor"] = 2
        self.data['resource_group'] = self.single_vms.id
        serializer = TransformerSerializer(instance=self.vcpu_from_core_transformer, data=self.data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.core_transformer.refresh_from_db()
        self.assertEqual(self.core_transformer.total_consumed, consumption_before / 2)
