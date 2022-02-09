from profiles.models import Quota, BillingGroup, QuotaBinding
from resource_tracker.models import ResourceGroupAttributeDefinition, Resource
from service_catalog.models import Instance
from tests.test_resource_tracker.base_test_resource_tracker import BaseTestResourceTracker
from Squest.utils.disconnect_signals import skip_auto_calculation


class BaseTestQuota(BaseTestResourceTracker):

    @skip_auto_calculation
    def setUp(self):
        super(BaseTestQuota, self).setUp()
        self.cpu_attributes = ResourceGroupAttributeDefinition.objects.filter(name__icontains='cpu')
        self.memory_attributes = ResourceGroupAttributeDefinition.objects.filter(name__icontains='memory')
        self.test_quota_attribute_cpu = Quota.objects.create(name="CPU")
        self.test_quota_attribute_memory = Quota.objects.create(name="memory")
        for attribute in self.cpu_attributes:
            self.test_quota_attribute_cpu.attribute_definitions.add(attribute.id)
        for attribute in self.memory_attributes:
            self.test_quota_attribute_memory.attribute_definitions.add(attribute.id)
        for billing in BillingGroup.objects.all():
            QuotaBinding.objects.create(
                billing_group=billing,
                quota=self.test_quota_attribute_cpu
            )
            QuotaBinding.objects.create(
                billing_group=billing,
                quota=self.test_quota_attribute_memory
            )
        self.test_quota_binding = self.test_billing_group.quota_bindings.first()
        billing_count = BillingGroup.objects.count()
        i = 0
        for resource in Resource.objects.all():
            instance = Instance.objects.create(
                name=f"test-{i}",
                billing_group=BillingGroup.objects.all()[i % billing_count],
            )
            resource.service_catalog_instance = instance
            resource.save()
            i += 1
