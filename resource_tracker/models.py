from django.db import models
from taggit.managers import TaggableManager

from service_catalog.models import Instance


class ExceptionResourceTracker:
    class AttributeAlreadyExist(Exception):
        def __init__(self, resource_group_name, attribute_name):
            super().__init__(f"Attribute {attribute_name} already exist in {resource_group_name}")


class ResourceGroup(models.Model):
    name = models.CharField(max_length=100,
                            blank=False,
                            unique=True)

    tags = TaggableManager()

    def __str__(self):
        return self.name

    def add_attribute_definition(self, name, produce_for=None, consume_from=None):

        obj = ResourceGroupAttributeDefinition.objects.filter(name=name, resource_group_definition=self)

        if len(obj) == 0:
            attribute = self.attribute_definitions.create(name=name, produce_for=produce_for, consume_from=consume_from)
            attribute.save()
            self.init_attribute(attribute)
            return attribute
        else:
            raise ExceptionResourceTracker.AttributeAlreadyExist(resource_group_name=self.name, attribute_name=name)

    def init_attribute(self, attribute):
        for resource in self.resources.all():
            resource.set_attribute(attribute, 0)

    def create_resource(self, name) -> 'Resource':
        resource, _ = self.resources.get_or_create(name=name)
        for attribute in self.attribute_definitions.all():
            resource.set_attribute(attribute_type=attribute, value=0)
        return resource

    def get_sum_value_by_attribute(self, attribute_type):
        return sum([resource.attributes.get(attribute_type=attribute_type).value for resource in self.resources.all()])


class Resource(models.Model):
    name = models.CharField(max_length=100,
                            blank=False,
                            unique=True)
    resource_group = models.ForeignKey(ResourceGroup,
                                       on_delete=models.SET_NULL,
                                       related_name='resources',
                                       related_query_name='resource',
                                       null=True)

    service_catalog_instance = models.ForeignKey(Instance,
                                                 on_delete=models.SET_NULL,
                                                 related_name='resources',
                                                 related_query_name='resource',
                                                 null=True)

    tags = TaggableManager()

    def __str__(self):
        return f"{self.name}[" + ",".join([f"{attribute.attribute_type.name}: {attribute.value}"
                                           for attribute in self.attributes.all()]) + "]"

    def set_attribute(self, attribute_type, value=0):
        attribute, _ = self.attributes.get_or_create(attribute_type=attribute_type)
        attribute.value = value
        attribute.save()


class ResourceGroupAttributeDefinition(models.Model):
    name = models.CharField(max_length=100,
                            blank=False)
    resource_group_definition = models.ForeignKey(ResourceGroup,
                                                  on_delete=models.PROTECT,
                                                  related_name='attribute_definitions',
                                                  related_query_name='attribute_definition',
                                                  null=True)
    consume_from = models.ForeignKey('ResourcePoolAttributeDefinition',
                                     on_delete=models.PROTECT,
                                     related_name='consumers',
                                     related_query_name='consumer',
                                     null=True)
    produce_for = models.ForeignKey('ResourcePoolAttributeDefinition',
                                    on_delete=models.PROTECT,
                                    related_name='producers',
                                    related_query_name='producer',
                                    null=True)

    def __str__(self):
        return f"{self.resource_group_definition} - {self.name}"

    def get_total_resource(self):
        total = 0
        for resource in self.resource_group_definition.resources.all():
            try:
                total += resource.attributes.get(attribute_type=self).value
            except ResourceAttribute.DoesNotExist:
                pass
        return total

    class Meta:
        unique_together = ('name', 'resource_group_definition',)


class ResourcePool(models.Model):
    name = models.CharField(max_length=100,
                            blank=False,
                            unique=True)

    tags = TaggableManager()

    def __str__(self):
        return self.name

    def add_attribute_definition(self, name):
        return self.attribute_definitions.create(name=name)


class ResourceAttribute(models.Model):
    value = models.PositiveIntegerField(default=0)

    resource = models.ForeignKey(Resource,
                                 on_delete=models.CASCADE,
                                 related_name='attributes',
                                 related_query_name='attribute',
                                 null=True)

    attribute_type = models.ForeignKey(ResourceGroupAttributeDefinition,
                                       on_delete=models.CASCADE,
                                       related_name='attribute_types',
                                       related_query_name='attribute_type',
                                       null=True)

    def __str__(self):
        return str(self.value)


class ResourcePoolAttributeDefinition(models.Model):
    # Resource Pool Attribute are linked to ResourceGroupAttributeDefinition
    # A ResourcePoolAttribute have "consumers" and "producers"
    name = models.CharField(max_length=100,
                            blank=False)
    resource_pool = models.ForeignKey(ResourcePool,
                                      on_delete=models.PROTECT,
                                      related_name='attribute_definitions',
                                      related_query_name='attribute_definition',
                                      null=True)
    over_commitment_producers = models.FloatField(default=1)
    over_commitment_consumers = models.FloatField(default=1)

    class Meta:
        unique_together = ('name', 'resource_pool',)

    def __str__(self):
        return f"{self.resource_pool.name} - {self.name}"

    def add_producers(self, resource: ResourceGroupAttributeDefinition):
        resource.produce_for = self
        resource.save()

    def add_consumers(self, resource: ResourceGroupAttributeDefinition):
        resource.consume_from = self
        resource.save()

    def get_total_produced(self):
        total_produced = 0
        for producer in self.producers.all():  # producer == ResourceGroupAttributeDefinition
            # For all ResourceGroup that produce for my attribute
            for resource in producer.resource_group_definition.resources.all():
                # For all resource in the resource group, get the good attribute
                try:
                    total_produced += resource.attributes.get(attribute_type=producer).value
                except ResourceAttribute.DoesNotExist:
                    pass
        return total_produced * self.over_commitment_producers

    def get_total_consumed(self):
        total_consumed = 0
        for consumer in self.consumers.all():  # consumer == ResourceGroupAttributeDefinition
            for resource in consumer.resource_group_definition.resources.all():
                try:
                    total_consumed += resource.attributes.get(attribute_type=consumer).value
                except ResourceAttribute.DoesNotExist:
                    pass
        return total_consumed * self.over_commitment_consumers

    def get_percent_consumed(self):
        percent_consumed = 0
        try:
            percent_consumed = (self.get_total_consumed() * 100) / self.get_total_produced()
        except ZeroDivisionError:
            pass
        return round(percent_consumed)

    def get_total_produced_by(self, producer):
        total_produced = 0
        for resource in producer.resource_group_definition.resources.all():
            try:
                total_produced += resource.attributes.get(attribute_type=producer).value
            except ResourceAttribute.DoesNotExist:
                pass
        return total_produced * self.over_commitment_producers

    def get_total_consumed_by(self, consumer):
        total_consumed = 0
        for resource in consumer.resource_group_definition.resources.all():
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
