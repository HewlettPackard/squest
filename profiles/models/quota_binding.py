from django.db.models import Model, ForeignKey, CASCADE, FloatField
from django.db.models.signals import post_save
from django.dispatch import receiver

from profiles.models import BillingGroup
from profiles.models.quota import Quota
from service_catalog import tasks


class QuotaBinding(Model):
    class Meta:
        unique_together = ('billing_group', 'quota',)
    limit = FloatField(default=0)
    consumed = FloatField(default=0)
    billing_group = ForeignKey(
        to=BillingGroup,
        blank=False,
        null=False,
        on_delete=CASCADE,
        related_name='quota_bindings'
    )
    quota = ForeignKey(
        to=Quota,
        blank=False,
        null=False,
        on_delete=CASCADE,
        related_name='quota_bindings'
    )

    @property
    def available(self):
        return self.limit - self.consumed

    @property
    def percentage(self):
        if self.limit == 0:
            return None
        percent_consumed = (self.consumed * 100) / self.limit
        return round(percent_consumed)

    def refresh_consumed(self):
        consumed = 0
        for instance in self.billing_group.instances.all():
            for resource in instance.resources.all():
                for attribute in resource.attributes.all():
                    if attribute.attribute_type in self.quota.attribute_definitions.all():
                        consumed += attribute.value
        self.consumed = consumed
        self.save()

    def calculate_consumed(self, delta):
        self.consumed += delta
        self.save()

    def update_consumed_with_resources(self, resources_to_add=None, resources_to_remove=None):
        delta = 0
        if resources_to_add:
            for resource in resources_to_add:
                for attribute in resource.attributes.all():
                    if attribute.attribute_type in self.quota.attribute_definitions.all():
                        delta += attribute.value
        if resources_to_remove:
            for resource in resources_to_remove:
                for attribute in resource.attributes.all():
                    if attribute.attribute_type in self.quota.attribute_definitions.all():
                        delta -= attribute.value
        self.calculate_consumed(delta)

    def __str__(self):
        return f"{self.quota.name} = {self.consumed} (limit: {self.limit})"


@receiver(post_save, sender=QuotaBinding)
def get_consumed(sender, instance, created, **kwargs):
    if created:
        tasks.async_quota_binding_calculate_consumed.delay(instance.id, None)
