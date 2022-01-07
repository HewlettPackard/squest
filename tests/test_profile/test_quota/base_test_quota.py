from profiles.models import QuotaAttributeDefinition, BillingGroup, QuotaBinding
from resource_tracker.models import ResourceGroupAttributeDefinition, Resource
from service_catalog.models import Instance
from tests.test_resource_tracker.base_test_resource_tracker import BaseTestResourceTracker
from tests.utils import skip_auto_calculation


class BaseTestQuota(BaseTestResourceTracker):

    @skip_auto_calculation
    def setUp(self):
        super(BaseTestQuota, self).setUp()
        self.test_quota_attribute_cpu = QuotaAttributeDefinition.objects.create(name="CPU")
        self.test_quota_attribute_memory = QuotaAttributeDefinition.objects.create(name="memory")
        for attribute in ResourceGroupAttributeDefinition.objects.filter(name__icontains='cpu'):
            self.test_quota_attribute_cpu.attribute_definitions.add(attribute.id)
        for attribute in ResourceGroupAttributeDefinition.objects.filter(name__icontains='memory'):
            self.test_quota_attribute_memory.attribute_definitions.add(attribute.id)
        for billing in BillingGroup.objects.all():
            QuotaBinding.objects.create(
                billing_group=billing,
                quota_attribute_definition=self.test_quota_attribute_cpu
            )
            QuotaBinding.objects.create(
                billing_group=billing,
                quota_attribute_definition=self.test_quota_attribute_memory
            )
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
