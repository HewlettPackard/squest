from django.contrib.auth.models import User
from django.db import models


class BillingGroup(models.Model):
    name = models.CharField(max_length=100,
                            blank=False,
                            unique=True)
    user_set = models.ManyToManyField(
        User,
        blank=True,
        help_text="The users in this billing group.",
        related_name="billing_groups",
        related_query_name="billing_groups",
        verbose_name="billing groups"
    )

    def __str__(self):
        return self.name

    def quota_bindings_update_consumed(self):
        for binding in self.quota_bindings.all():
            binding.refresh_consumed()

    def quota_bindings_remove_instance(self, instance):
        for resource in instance.resources.all():
            self.quota_bindings_remove_resource(resource)

    def quota_bindings_add_instance(self, instance):
        for resource in instance.resources.all():
            self.quota_bindings_add_resource(resource)

    def quota_bindings_remove_resource(self, resource):
        for binding in self.quota_bindings.all():
            for attribute in resource.attributes.filter(attribute_type__in=binding.quota.attribute_definitions.all()):
                binding.calculate_consumed(-attribute.value)

    def quota_bindings_add_resource(self, resource):
        for binding in self.quota_bindings.all():
            for attribute in resource.attributes.filter(attribute_type__in=binding.quota.attribute_definitions.all()):
                binding.calculate_consumed(attribute.value)
