from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from resource_tracker.models import ResourceGroupAttributeDefinition, ResourceAttribute


class ResourcePoolAttributeDefinition(models.Model):
    class Meta:
        unique_together = ('name', 'resource_pool',)
    # Resource Pool Attribute are linked to ResourceGroupAttributeDefinition
    # A ResourcePoolAttribute have "consumers" and "producers"
    name = models.CharField(max_length=100,
                            blank=False)
    resource_pool = models.ForeignKey('ResourcePool',
                                      on_delete=models.CASCADE,
                                      related_name='attribute_definitions',
                                      related_query_name='attribute_definition',
                                      null=True)
    over_commitment_producers = models.FloatField(default=1)
    over_commitment_consumers = models.FloatField(default=1)
    total_consumed = models.IntegerField(default=0)
    total_produced = models.IntegerField(default=0)
    yellow_threshold_percent_consumed = models.IntegerField(
        default=80,
        blank=True,
        verbose_name="Yellow threshold percent consumed",
        help_text="Threshold at which the color changes to yellow. Threshold is reverse when the red threshold is lower"
                  " than the yellow threshold."
    )
    red_threshold_percent_consumed = models.IntegerField(
        default=90,
        blank=True,
        verbose_name="Red threshold percent consumed",
        help_text="Threshold at which the color changes to red. Threshold is reverse when the red threshold is lower"
                  " than the yellow threshold."
    )

    def __str__(self):
        return f"{self.resource_pool.name} - {self.name}"

    @property
    def available(self):
        return self.total_produced - self.total_consumed

    @property
    def percent_consumed(self):
        if self.total_produced == 0:
            return "N/A"
        return round(self.total_consumed * 100 / self.total_produced)

    @property
    def percent_available(self):
        if self.total_produced == 0:
            return "N/A"
        return round(100 - self.percent_consumed)

    @property
    def progress_bar_color(self):
        reversed_color = self.yellow_threshold_percent_consumed < self.red_threshold_percent_consumed
        if isinstance(self.percent_consumed, int):
            if int(self.percent_consumed) < self.yellow_threshold_percent_consumed and not int(self.percent_consumed) > self.red_threshold_percent_consumed:
                return "green" if reversed_color else "red"
            if int(self.percent_consumed) > self.red_threshold_percent_consumed and not int(self.percent_consumed) < self.yellow_threshold_percent_consumed:
                return "red" if reversed_color else "green"
            return "yellow"
        return "gray"

    def add_producers(self, resource: ResourceGroupAttributeDefinition):
        resource.produce_for = self
        resource.save()

    def add_consumers(self, resource: ResourceGroupAttributeDefinition):
        resource.consume_from = self
        resource.save()

    def calculate_produced(self, delta):
        self.total_produced += delta * self.over_commitment_producers
        self.save()

    def calculate_total_produced(self):
        total_produced = 0
        for producer in self.producers.all():  # producer == ResourceGroupAttributeDefinition
            # For all ResourceGroup that produce for my attribute
            for resource in producer.resource_group.resources.all():
                # For all resource in the resource group, get the good attribute
                try:
                    total_produced += resource.attributes.get(attribute_type=producer).value
                except ResourceAttribute.DoesNotExist:
                    pass
        self.total_produced = total_produced * self.over_commitment_producers
        self.save()

    def calculate_consumed(self, delta):
        self.total_consumed += delta * self.over_commitment_consumers
        self.save()

    def calculate_total_consumed(self):
        total_consumed = 0
        for consumer in self.consumers.all():  # consumer == ResourceGroupAttributeDefinition
            for resource in consumer.resource_group.resources.all():
                try:
                    total_consumed += resource.attributes.get(attribute_type=consumer).value
                except ResourceAttribute.DoesNotExist:
                    pass
        self.total_consumed = total_consumed * self.over_commitment_consumers
        self.save()

    def get_total_produced_by(self, producer):
        total_produced = 0
        for resource in producer.resource_group.resources.all():
            try:
                total_produced += resource.attributes.get(attribute_type=producer).value
            except ResourceAttribute.DoesNotExist:
                pass
        return total_produced * self.over_commitment_producers

    def get_total_consumed_by(self, consumer):
        total_consumed = 0
        for resource in consumer.resource_group.resources.all():
            try:
                total_consumed += resource.attributes.get(attribute_type=consumer).value
            except ResourceAttribute.DoesNotExist:
                pass
        return total_consumed * self.over_commitment_consumers

    def remove_all_producer(self):
        for producer in self.producers.all():
            producer.produce_for = None
            producer.save()

    def remove_all_consumer(self):
        for consumer in self.consumers.all():
            consumer.consume_from = None
            consumer.save()


@receiver(pre_save, sender=ResourcePoolAttributeDefinition)
def on_change(sender, instance, **kwargs):
    if instance.id:  # if edit
        old = ResourcePoolAttributeDefinition.objects.get(id=instance.id)
        if instance.over_commitment_consumers != old.over_commitment_consumers:
            instance.total_consumed = (instance.total_consumed/old.over_commitment_consumers) * instance.over_commitment_consumers
        if instance.over_commitment_producers != old.over_commitment_producers:
            instance.total_produced = (instance.total_produced/old.over_commitment_producers) * instance.over_commitment_producers
