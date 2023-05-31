from resource_tracker_v2.forms.transformer_form import TransformerForm
from resource_tracker_v2.models import AttributeDefinition, Transformer, ResourceGroup
from tests.test_resource_tracker_v2.base_test_resource_tracker_v2 import BaseTestResourceTrackerV2


class TransformerFormTests(BaseTestResourceTrackerV2):

    def setUp(self):
        super(TransformerFormTests, self).setUp()
        self.disk_att = AttributeDefinition.objects.create(name="disk")
        self.parameters = {
            "source_resource_group": self.single_vms,
        }

    def test_create_transformer_no_consumption(self):
        number_transformer_before = Transformer.objects.count()

        data = {
            "attribute_definition": self.disk_att.id
        }
        form = TransformerForm(data, **self.parameters)
        form.is_valid()
        form.save()
        self.assertEqual(number_transformer_before + 1, Transformer.objects.count())

    def test_create_transformer_with_consumption(self):
        number_transformer_before = Transformer.objects.count()
        data = {
            "attribute_definition": self.disk_att.id,
            "consume_from_resource_group": self.cluster.id,
            "consume_from_attribute_definition": self.three_par_attribute.id,
        }
        form = TransformerForm(data, **self.parameters)
        self.assertTrue(form.is_valid())
        new_transformer = form.save()
        self.assertEqual(number_transformer_before + 1, Transformer.objects.count())
        self.assertEqual(new_transformer.consume_from_resource_group, self.cluster)
        self.assertEqual(new_transformer.consume_from_attribute_definition, self.three_par_attribute)
        self.assertEqual(new_transformer.factor, 1)

    def test_cannot_create_transformer_with_target_rg_and_no_target_attribute(self):
        data = {
            "attribute_definition": self.disk_att.id,
            "consume_from_resource_group": self.cluster.id,
        }
        form = TransformerForm(data, **self.parameters)
        self.assertFalse(form.is_valid())
        self.assertIsNotNone(form.errors["consume_from_attribute_definition"])

    def test_cannot_create_transformer_with_no_target_rg_and_target_attribute(self):
        data = {
            "attribute_definition": self.disk_att.id,
            "consume_from_attribute_definition": self.cluster.id,
        }
        form = TransformerForm(data, **self.parameters)
        self.assertFalse(form.is_valid())
        self.assertIsNotNone(form.errors["consume_from_resource_group"])

    def test_transformer_exist_already_on_selected_attribute(self):
        data = {
            "attribute_definition": self.vcpu_attribute.id,
        }
        form = TransformerForm(data, **self.parameters)
        self.assertFalse(form.is_valid())
        self.assertIsNotNone(form.errors["attribute_definition"])

    def test_invalid_target_attribute_in_transformer(self):
        data = {
            "attribute_definition": self.disk_att.id,
            "consume_from_resource_group": self.cluster.id,
            "consume_from_attribute_definition": self.vcpu_attribute.id,
        }
        form = TransformerForm(data, **self.parameters)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["consume_from_attribute_definition"], [f"Selected attribute '{self.vcpu_attribute.name}' is "
                                                               f"not a valid attribute of the resource group '{self.cluster.name}'"])

    def test_can_link_attribute_to_multiple_same_attribute_def_from_different_rg(self):
        """
        ┌───────────┐       ┌───────────┐
        │ Single VMs│       │ Other_VMs │
        │           │       │           │
        │   vCPU    │       │  vCPU     │
        └────┬──────┘       └─────┬─────┘
             │                    │
             │  ┌───────────────┐ │
             │  │  ocp_project  │ │
             │  │               │ │
             └──┼─►request.vcpu │ │
                │  other_field  ◄─┘
                └───────────────┘
        """
        other_vms = ResourceGroup.objects.create(name="other_vms")
        Transformer.objects.create(resource_group=other_vms, attribute_definition=self.vcpu_attribute)
        other_field = AttributeDefinition.objects.create(name="other_field")

        parameters = {
            "source_resource_group": self.ocp_projects,
        }
        data = {
            "attribute_definition": other_field.id,
            "consume_from_resource_group": other_vms.id,
            "consume_from_attribute_definition": self.vcpu_attribute.id,
        }
        number_transformer_before = Transformer.objects.count()
        form = TransformerForm(data, **parameters)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(number_transformer_before + 1, Transformer.objects.count())

    def test_edit_transformer_consumption(self):
        parameters = {
            "source_resource_group": self.ocp_projects,
            "instance": self.request_cpu_from_vcpu
        }
        data = {
            "consume_from_resource_group": self.cluster.id,
            "consume_from_attribute_definition": self.core_attribute.id,
        }

        self.request_cpu_from_vcpu.refresh_from_db()
        self.assertEqual(self.request_cpu_from_vcpu.consume_from_resource_group, self.single_vms)
        self.assertEqual(self.request_cpu_from_vcpu.consume_from_attribute_definition, self.vcpu_attribute)
        form = TransformerForm(data, **parameters)
        self.assertTrue(form.is_valid())
        form.save()
        self.request_cpu_from_vcpu.refresh_from_db()
        self.assertEqual(self.request_cpu_from_vcpu.consume_from_resource_group, self.cluster)
        self.assertEqual(self.request_cpu_from_vcpu.consume_from_attribute_definition, self.core_attribute)

    def test_edit_transformer_consumption_non_valid_target_attribute(self):
        parameters = {
            "source_resource_group": self.ocp_projects,
            "instance": self.request_cpu_from_vcpu
        }
        data = {
            "consume_from_resource_group": self.cluster.id,
            "consume_from_attribute_definition": self.vcpu_attribute.id,
        }

        form = TransformerForm(data, **parameters)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["consume_from_attribute_definition"],
            [f"Selected attribute '{self.vcpu_attribute.name}' is "
             f"not a valid attribute of the resource group '{self.cluster.name}'"])

    def test_cannot_create_circular_loop_when_adding_consumer(self):
        data = {
            "attribute_definition": self.core_attribute.id,
            "consume_from_resource_group": self.ocp_projects.id,
            "consume_from_attribute_definition": self.request_cpu.id,
        }
        parameters = {
            "source_resource_group": self.cluster,
        }
        form = TransformerForm(instance=self.core_transformer, data=data, **parameters)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["consume_from_attribute_definition"],
            [f"Circular loop detected on resource "
             f"group '{self.cluster.name}'"])
