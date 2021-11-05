from django.db import models
from django.db.models.signals import post_save
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

    def __str__(self):
        return f"{self.resource_pool.name} - {self.name}"

    def add_producers(self, resource: ResourceGroupAttributeDefinition):
        previous_producer = None
        if resource.produce_for is not None:
            previous_producer = resource.produce_for
        resource.produce_for = self
        resource.save()
        self.calculate_total_produced()
        if previous_producer is not None:
            previous_producer.calculate_total_produced()

    def add_consumers(self, resource: ResourceGroupAttributeDefinition):
        previous_consumer = None
        if resource.consume_from is not None:
            previous_consumer = resource.consume_from
        resource.consume_from = self
        resource.save()
        self.calculate_total_consumed()
        if previous_consumer is not None:
            previous_consumer.calculate_total_consumed()

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

    def get_percent_available_human_readable(self):
        if self.total_produced == 0:
            return ""
        return f"({round(100 - self.get_percent_consumed())}%)"

    def get_percent_consumed(self):
        if self.total_produced == 0:
            return "N/A"
        percent_consumed = 0
        try:
            percent_consumed = (self.total_consumed * 100) / self.total_produced
        except ZeroDivisionError:
            pass
        return round(percent_consumed)

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


def on_change(sender, instance, created, **kwargs):
    post_save.disconnect(on_change, sender=sender)  # prevent post save recursion
    instance.calculate_total_consumed()
    instance.calculate_total_produced()
    instance.save()
    post_save.connect(on_change, sender=sender)


post_save.connect(on_change, sender=ResourcePoolAttributeDefinition)
