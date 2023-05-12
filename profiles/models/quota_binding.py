from django.db.models import Model, ForeignKey, CASCADE, FloatField, IntegerField
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
    yellow_threshold_percent = IntegerField(
        default=80,
        blank=True,
        verbose_name="Yellow threshold percent consumed",
        help_text="Threshold at which the color changes to yellow. Threshold is reverse when the red threshold is lower"
                  " than the yellow threshold."
    )
    red_threshold_percent = IntegerField(
        default=90,
        blank=True,
        verbose_name="Red threshold percent consumed",
        help_text="Threshold at which the color changes to red. Threshold is reverse when the red threshold is lower"
                  " than the yellow threshold."
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

    @property
    def progress_bar_color(self):
        reversed_color = self.yellow_threshold_percent < self.red_threshold_percent
        if isinstance(self.percentage, int):
            if int(self.percentage) < self.yellow_threshold_percent and not int(self.percentage) > self.red_threshold_percent:
                return "green" if reversed_color else "red"
            if int(self.percentage) > self.red_threshold_percent and not int(self.percentage) < self.yellow_threshold_percent:
                return "red" if reversed_color else "green"
            return "yellow"
        return "gray"

    def refresh_consumed(self):
        consumed = 0
        for instance in self.billing_group.instances.all():
            for resource in instance.resources_v1.all():
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
