from resource_tracker_v2.forms.resource_group_link_form import ResourceGroupLinkForm
from resource_tracker_v2.models import AttributeDefinition, Transformer, ResourceGroup
from tests.test_resource_tracker_v2.base_test_resource_tracker_v2 import BaseTestResourceTrackerV2


class ResourceGroupLinkFormTests(BaseTestResourceTrackerV2):

    def setUp(self):
        super(ResourceGroupLinkFormTests, self).setUp()
        self.disk_att = AttributeDefinition.objects.create(name="disk")
        self.parameters = {
            "source_resource_group": self.single_vms,
        }

    def test_create_resource_group_link_no_transformer(self):
        number_attribute_before = self.single_vms.attribute_definitions.count()

        data = {
            "source_attribute_id": self.disk_att.id
        }
        form = ResourceGroupLinkForm(data, **self.parameters)
        form.is_valid()
        form.save()
        self.single_vms.refresh_from_db()
        self.assertEqual(number_attribute_before + 1, self.single_vms.attribute_definitions.count())

    def test_create_resource_group_link_with_transformer(self):
        number_attribute_before = self.single_vms.attribute_definitions.count()
        number_transformer_before = Transformer.objects.count()
        data = {
            "source_attribute_id": self.disk_att.id,
            "consume_from_resource_group_id": self.cluster.id,
            "consume_from_attribute_id": self.three_par_attribute.id,
        }
        form = ResourceGroupLinkForm(data, **self.parameters)
        form.is_valid()
        form.save()
        self.single_vms.refresh_from_db()
        self.assertEqual(number_attribute_before + 1, self.single_vms.attribute_definitions.count())
        self.assertEqual(number_transformer_before + 1, Transformer.objects.count())

    def test_transformer_exist_already_on_selected_attribute(self):
        data = {
            "source_attribute_id": self.vcpu_attribute.id,
        }
        form = ResourceGroupLinkForm(data, **self.parameters)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["source_attribute_id"], [f"Select a valid choice. {self.vcpu_attribute.id} is not one of the available choices."]
        )

    def test_invalid_target_resource_group_in_transformer(self):
        data = {
            "source_attribute_id": self.disk_att.id,
            "consume_from_resource_group_id": 9999999,
            "consume_from_attribute_id": self.three_par_attribute.id,
        }
        form = ResourceGroupLinkForm(data, **self.parameters)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["consume_from_resource_group_id"], [f"Select a valid choice. 9999999 is not one of the available choices."])

    def test_invalid_target_attribute_in_transformer(self):
        data = {
            "source_attribute_id": self.disk_att.id,
            "consume_from_resource_group_id": self.cluster.id,
            "consume_from_attribute_id": 9999999,
        }
        form = ResourceGroupLinkForm(data, **self.parameters)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["consume_from_attribute_id"], [f"Select a valid choice. 9999999 is not one of the available choices."])

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
        other_vms.attribute_definitions.add(self.vcpu_attribute)

        other_field = AttributeDefinition.objects.create(name="other_field")

        parameters = {
            "source_resource_group": self.ocp_projects,
        }
        data = {
            "source_attribute_id": other_field.id,
            "consume_from_resource_group_id": other_vms.id,
            "consume_from_attribute_id": self.vcpu_attribute.id,
        }
        number_transformer_before = Transformer.objects.count()
        form = ResourceGroupLinkForm(data, **parameters)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(number_transformer_before + 1, Transformer.objects.count())
