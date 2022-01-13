from profiles.models import BillingGroup, QuotaBinding, Quota
from resource_tracker.models import Resource, ResourceGroup
from service_catalog.models import Instance
from tests.test_profile.test_quota.base_test_quota import BaseTestQuota


class TestQuotaModel(BaseTestQuota):

    def setUp(self):
        super(TestQuotaModel, self).setUp()

    def test_get_available(self):
        quota_binding = self.test_billing_group.quota_bindings.first()
        quota_binding.limit = 100
        self.assertEqual(quota_binding.available, 100 - quota_binding.consumed)

    def test_get_percentage(self):
        quota_binding = self.test_billing_group.quota_bindings.first()
        quota_binding.limit = 100
        self.assertEqual(quota_binding.percentage, quota_binding.consumed)

    def test_update_consumed(self):
        billing_group = BillingGroup.objects.create(name='test_update')
        instance = Instance.objects.create(name='test_update', billing_group=billing_group)
        instance_2 = Instance.objects.create(name='test_update_2', billing_group=billing_group)
        resource_group = ResourceGroup.objects.create(name='test_update')
        attribute_definition = resource_group.add_attribute_definition('test_update')
        quota_attribute = Quota.objects.create(name='test_update')
        quota_attribute.attribute_definitions.add(attribute_definition)
        quota_binding = QuotaBinding.objects.create(billing_group=billing_group,
                                                    quota=quota_attribute)
        quota_binding.refresh_from_db()
        self.assertEqual(quota_binding.consumed, 0)
        resource = Resource.objects.create(name='test_update_1', resource_group=resource_group,
                                           service_catalog_instance=instance)
        resource.set_attribute(attribute_definition, 16)
        resource_2 = Resource.objects.create(name='test_update_2', resource_group=resource_group,
                                             service_catalog_instance=instance)
        resource_2.set_attribute(attribute_definition, 16)
        quota_binding.refresh_from_db()
        self.assertEqual(quota_binding.consumed, 16 * 2)
        resource_3 = Resource.objects.create(name='test_update_3', resource_group=resource_group,
                                             service_catalog_instance=instance_2)
        resource_3.set_attribute(attribute_definition, 16)
        resource_4 = Resource.objects.create(name='test_update_4', resource_group=resource_group,
                                             service_catalog_instance=instance_2)
        resource_4.set_attribute(attribute_definition, 16)
        quota_binding.refresh_from_db()
        self.assertEqual(quota_binding.consumed, 4 * 16)

    def test_get_percentage_without_limit(self):
        quota_binding = self.test_billing_group.quota_bindings.first()
        quota_binding.limit = 0
        self.assertEqual(quota_binding.percentage, None)

    def test_consumed_updated_after_billing_group_changed_in_instance(self):
        instance_list = Instance.objects.exclude(billing_group=None)
        instance = instance_list.first()
        new_billing_group = BillingGroup.objects.exclude(id=instance.billing_group.id).first()
        self._check_billing_changed(instance, new_billing_group)
        self._check_billing_changed(instance, None)

    def _check_billing_changed(self, instance, new_billing_group):
        instance_cpu = 0
        for resource in instance.resources.all():
            for attribute in resource.attributes.all():
                if attribute.attribute_type in self.test_quota_attribute_cpu.attribute_definitions.all():
                    instance_cpu += attribute.value
        instance_memory = 0
        for resource in instance.resources.all():
            for attribute in resource.attributes.all():
                if attribute.attribute_type in self.test_quota_attribute_memory.attribute_definitions.all():
                    instance_memory += attribute.value
        old_billing_group = instance.billing_group
        old_consumed_cpu_old_billing_group = old_billing_group.quota_bindings.get(
            quota=self.test_quota_attribute_cpu).consumed
        old_consumed_memory_old_billing_group = old_billing_group.quota_bindings.get(
            quota=self.test_quota_attribute_memory).consumed;
        if new_billing_group:
            old_consumed_cpu_new_billing_group = new_billing_group.quota_bindings.get(
                quota=self.test_quota_attribute_cpu).consumed
            old_consumed_memory_new_billing_group = new_billing_group.quota_bindings.get(
                quota=self.test_quota_attribute_memory).consumed
        self.assertNotEqual(0, old_consumed_cpu_old_billing_group)
        self.assertNotEqual(0, old_consumed_memory_old_billing_group)
        if new_billing_group:
            self.assertNotEqual(0, old_consumed_cpu_new_billing_group)
            self.assertNotEqual(0, old_consumed_memory_new_billing_group)
        instance.billing_group = new_billing_group
        instance.save()
        self.assertEqual(old_consumed_cpu_old_billing_group - instance_cpu, old_billing_group.quota_bindings.get(
            quota=self.test_quota_attribute_cpu).consumed)
        self.assertEqual(old_consumed_memory_old_billing_group - instance_memory, old_billing_group.quota_bindings.get(
            quota=self.test_quota_attribute_memory).consumed)
        if new_billing_group:
            self.assertEqual(old_consumed_cpu_new_billing_group + instance_cpu, new_billing_group.quota_bindings.get(
                quota=self.test_quota_attribute_cpu).consumed)
            self.assertEqual(old_consumed_memory_new_billing_group + instance_memory,
                             new_billing_group.quota_bindings.get(
                                 quota=self.test_quota_attribute_memory).consumed)

    def test_consumed_updated_after_instance_changed_in_resource(self):
        instance_list = Instance.objects.exclude(billing_group=None)
        instance = instance_list.first()
        resource = instance.resources.first()
        resource_cpu = 0
        resource_memory = 0
        for attribute in resource.attributes.all():
            if attribute.attribute_type in self.test_quota_attribute_cpu.attribute_definitions.all():
                resource_cpu += attribute.value
        for attribute in resource.attributes.all():
            if attribute.attribute_type in self.test_quota_attribute_memory.attribute_definitions.all():
                resource_memory += attribute.value
        old_consumed_cpu = instance.billing_group.quota_bindings.get(
            quota=self.test_quota_attribute_cpu).consumed
        old_consumed_memory = instance.billing_group.quota_bindings.get(
            quota=self.test_quota_attribute_memory).consumed
        resource.service_catalog_instance = None
        resource.save()
        self.assertEqual(old_consumed_cpu - resource_cpu, instance.billing_group.quota_bindings.get(
            quota=self.test_quota_attribute_cpu).consumed)
        self.assertEqual(old_consumed_memory - resource_memory, instance.billing_group.quota_bindings.get(
            quota=self.test_quota_attribute_memory).consumed)
        resource.service_catalog_instance = instance
        resource.save()
        self.assertEqual(old_consumed_cpu, instance.billing_group.quota_bindings.get(
            quota=self.test_quota_attribute_cpu).consumed)
        self.assertEqual(old_consumed_memory, instance.billing_group.quota_bindings.get(
            quota=self.test_quota_attribute_memory).consumed)

    def test_consumed_updated_after_attribute_definitions_changed_in_quota_attribute(self):
        quota_binding = self.test_quota_attribute_cpu.quota_bindings.first()
        old_consumed = quota_binding.consumed
        attribute_definition = self.test_quota_attribute_cpu.attribute_definitions.first()
        value = 0
        for instance in quota_binding.billing_group.instances.all():
            for resource in instance.resources.all():
                for attribute in resource.attributes.all():
                    if attribute.attribute_type == attribute_definition:
                        value += attribute.value
        self.test_quota_attribute_cpu.attribute_definitions.remove(attribute_definition)
        quota_binding.refresh_from_db()
        self.assertEqual(old_consumed - value, quota_binding.consumed)
        self.test_quota_attribute_cpu.attribute_definitions.add(attribute_definition)
        quota_binding.refresh_from_db()
        self.assertEqual(old_consumed, quota_binding.consumed)
