from django.db import models


class ResourceGroup(models.Model):
    name = models.CharField(max_length=100,
                            blank=False,
                            unique=True)

    def add_attribute_definition(self, name):

        obj = ResourceGroupAttributeDefinition.objects.filter(name=name, resource_group_definition=self)

        if len(obj) == 0:
            self.attribute_definitions.create(name=name)
        elif len(obj) == 1:
            pass
        else:
            raise Exception(f"ResourceGroupAttributeDefinition with the same name({obj[0].name}) on "
                            f"the same group({obj[0].resource_group_definition})")

    def create_resource(self, name) -> 'Resource':
        resource, _ = self.resources.get_or_create(name=name)
        for attribute in self.attribute_definitions.all():
            resource.add_attribute(attribute.name)
        return resource

    def get_attribute(self, name):
        return sum([resource.attributes.get(name=name).value for resource in self.resources.all()])


class Resource(models.Model):
    name = models.CharField(max_length=100,
                            blank=False,
                            unique=True)
    resource_group = models.ForeignKey(ResourceGroup,
                                       on_delete=models.SET_NULL,
                                       related_name='resources',
                                       related_query_name='resource',
                                       null=True)

    def __str__(self):
        return f"{self.name}["+",".join([f"{attribute.name}: {attribute.value}"
                                         for attribute in self.attributes.all()]) + "]"

    def add_attribute(self, attribute):
        self.attributes.get_or_create(name=attribute)

    def set_attribute(self, attribute, value):
        attribute = self.attributes.get(name=attribute)
        attribute.value = value
        attribute.save()


class ResourceAttribute(models.Model):
    name = models.CharField(max_length=100,
                            blank=False)

    value = models.PositiveIntegerField(default=0)

    resource = models.ForeignKey(Resource,
                                 on_delete=models.CASCADE,
                                 related_name='attributes',
                                 related_query_name='attribute',
                                 null=True)

    def __str__(self):
        return str(self.value)


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

    class Meta:
        unique_together = ('name', 'resource_group_definition',)


class ResourcePool(models.Model):
    name = models.CharField(max_length=100,
                            blank=False,
                            unique=True)

    def add_attribute_definition(self, name):
        self.attributes_definition.create(name=name)


class ResourcePoolAttributeDefinition(models.Model):
    # Resource Pool Attribute are linked to ResourceGroupAttributeDefinition
    # A ResourcePoolAttribute have "consumers" and "producers"
    name = models.CharField(max_length=100,
                            blank=False)
    resource_pool = models.ForeignKey(ResourcePool,
                                      on_delete=models.PROTECT,
                                      related_name='attributes_definition',
                                      related_query_name='attribute_definition',
                                      null=True)

    def __str__(self):
        return "{} - {}".format(self.resource_pool.name, self.name)

    def add_producers(self, resource: ResourceGroupAttributeDefinition):
        resource.produce_for = self
        resource.save()

    def add_consumers(self, resource: ResourceGroupAttributeDefinition):
        resource.consume_from = self
        resource.save()

    def get_total_produced(self):
        total_produced = 0
        for producer in self.producers.all():
            # For all ResourceGroup that produce for my attribute
            attribute_name = producer.name
            for resource in producer.resource_group_definition.resources.all():
                # For all resource in the resource group, get the good attribute
                total_produced += resource.attributes.get(name=attribute_name).value
        return total_produced

    def get_total_consumed(self):
        total_consumed = 0
        for consumer in self.consumers.all():
            attribute_name = consumer.name
            for resource in consumer.resource_group_definition.resources.all():
                total_consumed += resource.attributes.get(name=attribute_name).value
        return total_consumed

    def get_percent_consumed(self):
        percent_consumed = 0
        try:
            percent_consumed = (self.get_total_consumed() * 100) / self.get_total_produced()
        except ZeroDivisionError:
            pass
        return round(percent_consumed)
