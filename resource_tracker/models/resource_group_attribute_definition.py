from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from resource_tracker.models.resource_attribute import ResourceAttribute


class ResourceGroupAttributeDefinition(models.Model):
    name = models.CharField(max_length=100,
                            blank=False)
    resource_group = models.ForeignKey('ResourceGroup',
                                       on_delete=models.CASCADE,
                                       related_name='attribute_definitions',
                                       related_query_name='attribute_definition',
                                       null=True)
    consume_from = models.ForeignKey('ResourcePoolAttributeDefinition',
                                     on_delete=models.SET_NULL,
                                     related_name='consumers',
                                     related_query_name='consumer',
                                     null=True)
    produce_for = models.ForeignKey('ResourcePoolAttributeDefinition',
                                    on_delete=models.SET_NULL,
                                    related_name='producers',
                                    related_query_name='producer',
                                    null=True)
    total_resource = models.IntegerField(default=0)

    help_text = models.CharField(max_length=100, default='', null=True, blank=True)

    def __str__(self):
        return f"{self.resource_group} - {self.name}"

    def calculate_resource(self, delta):
        self.total_resource += delta
        if self.consume_from is not None:
            self.consume_from.calculate_consumed(delta)
        if self.produce_for is not None:
            self.produce_for.calculate_produced(delta)
        self.save()

    def calculate_total_resource(self):
        total = 0
        for resource in self.resource_group.resources.all():
            try:
                total += resource.attributes.get(attribute_type=self).value
            except ResourceAttribute.DoesNotExist:
                pass
        self.total_resource = total
        # sync pool attributes
        if self.consume_from is not None:
            self.consume_from.calculate_total_consumed()
        if self.produce_for is not None:
            self.produce_for.calculate_total_produced()
        self.save()

    def edit(self, name, produce_for, consume_from, help_text):
        self.name = name
        self.consume_from = consume_from
        self.produce_for = produce_for
        self.help_text = help_text
        self.save()

    class Meta:
        unique_together = ('name', 'resource_group',)


@receiver(pre_save, sender=ResourceGroupAttributeDefinition)
def on_change(sender, instance, **kwargs):
    if instance.id:  # if edit
        old = ResourceGroupAttributeDefinition.objects.get(id=instance.id)
        if instance.consume_from != old.consume_from:
            if instance.consume_from:
                instance.consume_from.calculate_consumed(instance.total_resource)
            if old.consume_from:
                old.consume_from.calculate_consumed(-old.total_resource)
        if instance.produce_for != old.produce_for:
            if instance.produce_for:
                instance.produce_for.calculate_produced(instance.total_resource)
            if old.produce_for:
                old.produce_for.calculate_produced(-old.total_resource)
