from unittest import mock
from profiles.models import BillingGroup, QuotaBinding, Quota
from resource_tracker.models import Resource, ResourceGroup
from service_catalog.models import Instance
from service_catalog.tasks import async_resource_attribute_quota_bindings_update_consumed, \
    async_quota_bindings_update_consumed, async_quota_bindings_remove_instance, \
    async_quota_bindings_add_instance, async_quota_bindings_add_resource, \
    async_quota_bindings_remove_resource
from tests.test_profile.test_quota.base_test_quota import BaseTestQuota


class TestQuotaModel(BaseTestQuota):

    def setUp(self):
        super(TestQuotaModel, self).setUp()

    def test_get_available(self):
        self.quota_binding = self.test_billing_group.quota_bindings.first()
        self.quota_binding.limit = 100
        self.assertEqual(self.quota_binding.available, 100 - self.quota_binding.consumed)

    def test_get_percentage(self):
        self.quota_binding = self.test_billing_group.quota_bindings.first()
        self.quota_binding.limit = 100
        self.assertEqual(self.quota_binding.percentage, self.quota_binding.consumed)

    def test_get_percentage_without_limit(self):
        self.quota_binding = self.test_billing_group.quota_bindings.first()
        self.quota_binding.limit = 0
        self.assertEqual(self.quota_binding.percentage, None)

    def _set_up_update_consumed(self):
        self.billing_group = BillingGroup.objects.create(name='test_billing')
        self.billing_group_2 = BillingGroup.objects.create(name='test_billing_2')
        self.instance = Instance.objects.create(name='test_instance', billing_group=self.billing_group)
        self.instance_2 = Instance.objects.create(name='test_instance_2', billing_group=self.billing_group)
        self.instance_3 = Instance.objects.create(name='test_instance_3', billing_group=self.billing_group_2)
        self.instance_4 = Instance.objects.create(name='test_instance_4')
        self.resource_group = ResourceGroup.objects.create(name='test_rg')
        self.attribute_definition = self.resource_group.add_attribute_definition('test_ad')
        self.attribute_definition_2 = self.resource_group.add_attribute_definition('test_ad_2')
        self.quota_attribute = Quota.objects.create(name='test_update')
        self.quota_attribute.attribute_definitions.add(self.attribute_definition)
        self.quota_binding = QuotaBinding.objects.create(billing_group=self.billing_group, quota=self.quota_attribute)
        self.quota_binding_2 = QuotaBinding.objects.create(billing_group=self.billing_group_2,
                                                           quota=self.quota_attribute)
        self.quota_binding.refresh_from_db()
        self.assertEqual(self.quota_binding.consumed, 0)
        self.quota_binding_2.refresh_from_db()
        self.assertEqual(self.quota_binding_2.consumed, 0)
        # Create attributes linked to billing group
        self.resource = Resource.objects.create(name='test_update_1', resource_group=self.resource_group,
                                                service_catalog_instance=self.instance)
        self.resource.set_attribute(self.attribute_definition, 16)
        self.resource.set_attribute(self.attribute_definition_2, 32)
        self.resource_2 = Resource.objects.create(name='test_update_2', resource_group=self.resource_group,
                                                  service_catalog_instance=self.instance)
        self.resource_2.set_attribute(self.attribute_definition, 16)
        self.quota_binding.refresh_from_db()
        self.assertEqual(self.quota_binding.consumed, 16 * 2)
        self.quota_binding_2.refresh_from_db()
        self.assertEqual(self.quota_binding_2.consumed, 0)
        self.resource_3 = Resource.objects.create(name='test_update_3', resource_group=self.resource_group,
                                                  service_catalog_instance=self.instance_2)
        self.resource_3.set_attribute(self.attribute_definition, 16)
        self.resource_4 = Resource.objects.create(name='test_update_4', resource_group=self.resource_group,
                                                  service_catalog_instance=self.instance_2)
        self.resource_4.set_attribute(self.attribute_definition, 16)
        self.quota_binding.refresh_from_db()
        self.assertEqual(self.quota_binding.consumed, 4 * 16)
        self.quota_binding_2.refresh_from_db()
        self.assertEqual(self.quota_binding_2.consumed, 0)

    def test_instance_changed_in_resource_with_same_bg(self):
        self._set_up_update_consumed()
        self.resource_4.service_catalog_instance = self.instance
        with mock.patch("service_catalog.tasks.async_quota_bindings_add_resource.delay",
                        wraps=async_quota_bindings_add_resource):
            with mock.patch("service_catalog.tasks.async_quota_bindings_remove_resource.delay",
                            wraps=async_quota_bindings_remove_resource):
                self.resource_4.save()
        self.quota_binding.refresh_from_db()
        self.assertEqual(self.quota_binding.consumed, 4 * 16)
        self.quota_binding_2.refresh_from_db()
        self.assertEqual(self.quota_binding_2.consumed, 0)

    def test_instance_removed_in_resource(self):
        self._set_up_update_consumed()
        self.resource_4.service_catalog_instance = None
        with mock.patch("service_catalog.tasks.async_quota_bindings_add_resource.delay",
                        wraps=async_quota_bindings_add_resource):
            with mock.patch("service_catalog.tasks.async_quota_bindings_remove_resource.delay",
                            wraps=async_quota_bindings_remove_resource):
                self.resource_4.save()
        self.quota_binding.refresh_from_db()
        self.assertEqual(self.quota_binding.consumed, 3 * 16)
        self.quota_binding_2.refresh_from_db()
        self.assertEqual(self.quota_binding_2.consumed, 0)

    def test_instance_changed_in_resource_with_different_bg(self):
        self._set_up_update_consumed()
        self.resource_4.service_catalog_instance = self.instance_3
        with mock.patch("service_catalog.tasks.async_quota_bindings_add_resource.delay",
                        wraps=async_quota_bindings_add_resource):
            with mock.patch("service_catalog.tasks.async_quota_bindings_remove_resource.delay",
                            wraps=async_quota_bindings_remove_resource):
                self.resource_4.save()
        self.quota_binding.refresh_from_db()
        self.assertEqual(self.quota_binding.consumed, 3 * 16)
        self.quota_binding_2.refresh_from_db()
        self.assertEqual(self.quota_binding_2.consumed, 1 * 16)

    def test_instance_changed_in_resource_without_bg(self):
        self._set_up_update_consumed()
        self.resource_4.service_catalog_instance = self.instance_4
        with mock.patch("service_catalog.tasks.async_quota_bindings_add_resource.delay",
                        wraps=async_quota_bindings_add_resource):
            with mock.patch("service_catalog.tasks.async_quota_bindings_remove_resource.delay",
                            wraps=async_quota_bindings_remove_resource):
                self.resource_4.save()

        self.quota_binding.refresh_from_db()
        self.assertEqual(self.quota_binding.consumed, 3 * 16)
        self.quota_binding_2.refresh_from_db()
        self.assertEqual(self.quota_binding_2.consumed, 0)

    def test_bg_changed_in_instance(self):
        self._set_up_update_consumed()
        self.instance.billing_group = self.billing_group_2
        with mock.patch("service_catalog.tasks.async_quota_bindings_add_instance.delay", wraps=async_quota_bindings_add_instance):
            with mock.patch("service_catalog.tasks.async_quota_bindings_remove_instance.delay", wraps=async_quota_bindings_remove_instance):
                self.instance.save()
        self.quota_binding.refresh_from_db()
        self.assertEqual(self.quota_binding.consumed, 2 * 16)
        self.quota_binding_2.refresh_from_db()
        self.assertEqual(self.quota_binding_2.consumed, 2 * 16)

    def test_bg_removed_in_instance(self):
        self._set_up_update_consumed()
        self.instance.billing_group = None
        with mock.patch("service_catalog.tasks.async_quota_bindings_add_instance.delay", wraps=async_quota_bindings_add_instance):
            with mock.patch("service_catalog.tasks.async_quota_bindings_remove_instance.delay", wraps=async_quota_bindings_remove_instance):
                self.instance.save()
        self.quota_binding.refresh_from_db()
        self.assertEqual(self.quota_binding.consumed, 2 * 16)
        self.quota_binding_2.refresh_from_db()
        self.assertEqual(self.quota_binding_2.consumed, 0)

    def test_delete_rg(self):
        self._set_up_update_consumed()
        count = 0
        for resource in self.resource_group.resources.all():
            count += resource.attributes.count()
        with mock.patch(
                "service_catalog.tasks.async_resource_attribute_quota_bindings_update_consumed.delay", wraps=async_resource_attribute_quota_bindings_update_consumed):
            self.resource_group.delete()
        self.quota_binding.refresh_from_db()
        self.assertEqual(self.quota_binding.consumed, 0)
        self.quota_binding_2.refresh_from_db()
        self.assertEqual(self.quota_binding_2.consumed, 0)

    def test_delete_resource(self):
        self._set_up_update_consumed()
        with mock.patch(
                "service_catalog.tasks.async_resource_attribute_quota_bindings_update_consumed.delay", wraps=async_resource_attribute_quota_bindings_update_consumed):
            self.resource.delete()
        self.quota_binding.refresh_from_db()
        self.assertEqual(self.quota_binding.consumed, 3 * 16)
        self.quota_binding_2.refresh_from_db()
        self.assertEqual(self.quota_binding_2.consumed, 0)

    def test_delete_instance(self):
        self._set_up_update_consumed()
        count = 0
        for resource in self.instance.resources_v1.all():
            count += resource.attributes.count()
        with mock.patch(
                "service_catalog.tasks.async_resource_attribute_quota_bindings_update_consumed.delay", wraps=async_resource_attribute_quota_bindings_update_consumed):
            self.instance.delete()
        self.quota_binding.refresh_from_db()
        self.assertEqual(self.quota_binding.consumed, 2 * 16)
        self.quota_binding_2.refresh_from_db()
        self.assertEqual(self.quota_binding_2.consumed, 0)

    def test_attribute_definitions_added_in_quota_attribute(self):
        self._set_up_update_consumed()
        with mock.patch("service_catalog.tasks.async_quota_bindings_update_consumed.delay", wraps=async_quota_bindings_update_consumed):
            self.quota_attribute.attribute_definitions.add(self.attribute_definition_2)
        self.quota_binding.refresh_from_db()
        self.assertEqual(self.quota_binding.consumed, 4 * 16 + 32)
        self.quota_binding_2.refresh_from_db()
        self.assertEqual(self.quota_binding_2.consumed, 0)

    def test_attribute_definitions_removed_in_quota_attribute(self):
        self._set_up_update_consumed()
        with mock.patch("service_catalog.tasks.async_quota_bindings_update_consumed.delay", wraps=async_quota_bindings_update_consumed):
            self.quota_attribute.attribute_definitions.remove(self.attribute_definition)
        self.quota_binding.refresh_from_db()
        self.assertEqual(self.quota_binding.consumed, 0)
        self.quota_binding_2.refresh_from_db()
        self.assertEqual(self.quota_binding_2.consumed, 0)

    def test_tasks_quota_update_consumed(self):
        self._set_up_update_consumed()
        quota_binding_value = dict()
        for binding in self.quota_attribute.quota_bindings.all():
            quota_binding_value[binding.id] = binding.consumed
        wrong_value = 9999999
        for binding in self.quota_attribute.quota_bindings.all():
            binding.consumed = wrong_value
            binding.save()
        async_quota_bindings_update_consumed(self.quota_attribute.id)
        for binding in self.quota_attribute.quota_bindings.all():
            self.assertNotEqual(binding.consumed, wrong_value)
            self.assertEqual(binding.consumed, quota_binding_value.get(binding.id))

    def test_value_changed_in_resource_attribute(self):
        self._set_up_update_consumed()
        attribute = self.resource.attributes.first()
        with mock.patch("service_catalog.tasks.async_resource_attribute_quota_bindings_update_consumed.delay", wraps=async_resource_attribute_quota_bindings_update_consumed):
            attribute.value += 16
            attribute.save()
        self.quota_binding.refresh_from_db()
        self.assertEqual(self.quota_binding.consumed, 5 * 16)
        self.quota_binding_2.refresh_from_db()
        self.assertEqual(self.quota_binding_2.consumed, 0)
