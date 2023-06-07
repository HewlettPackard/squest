from django.db.models import Model, ForeignKey, CASCADE, FloatField, IntegerField, SET_NULL, CheckConstraint, F, Q
from django.urls import reverse

from resource_tracker_v2.models.attribute_definition import AttributeDefinition
from resource_tracker_v2.models.resource_attribute import ResourceAttribute
from resource_tracker_v2.models.resource_group import ResourceGroup


class Transformer(Model):

    class Meta:
        unique_together = (('resource_group', 'attribute_definition'),
                           ('resource_group', 'attribute_definition', 'consume_from_resource_group', 'consume_from_attribute_definition'))

        constraints = [
            CheckConstraint(name='cannot_consume_from_itself', check=~Q(resource_group=F('consume_from_resource_group')))
        ]

    resource_group = ForeignKey(ResourceGroup, null=False, on_delete=CASCADE,
                                related_name="transformers", related_query_name="transformer")
    attribute_definition = ForeignKey(AttributeDefinition, null=False, on_delete=CASCADE,
                                      related_name="transformers", related_query_name="transformer")
    consume_from_resource_group = ForeignKey(ResourceGroup, null=True, blank=True, on_delete=SET_NULL,
                                             related_name="consume_from_resource_group")
    consume_from_attribute_definition = ForeignKey(AttributeDefinition, null=True, blank=True, on_delete=SET_NULL,
                                                   related_name="consume_from_attribute_definition")
    factor = FloatField(null=True, blank=True)
    total_consumed = IntegerField(default=0)
    total_produced = IntegerField(default=0)
    yellow_threshold_percent_consumed = IntegerField(
        default=80,
        blank=True,
        verbose_name="Yellow threshold percent consumed",
        help_text="Threshold at which the color changes to yellow. Threshold is reverse when the red threshold is lower"
                  " than the yellow threshold."
    )
    red_threshold_percent_consumed = IntegerField(
        default=90,
        blank=True,
        verbose_name="Red threshold percent consumed",
        help_text="Threshold at which the color changes to red. Threshold is reverse when the red threshold is lower"
                  " than the yellow threshold."
    )

    def get_absolute_url(self):
        return reverse("resource_tracker:resource_group_attribute_list",
                       kwargs={"resource_group_id": self.resource_group.id})

    @classmethod
    def is_loop_consumption_detected(cls, source_resource_group, source_attribute, target_resource_group, target_attribute):
        source_transformer = Transformer.objects.filter(resource_group=source_resource_group,
                                                        attribute_definition=source_attribute)
        if not source_transformer.exists():
            return False
        source_transformer = source_transformer.first()

        target_transformer = Transformer.objects.filter(resource_group=target_resource_group,
                                                        attribute_definition=target_attribute)
        if not target_transformer.exists():
            return False
        target_transformer = target_transformer.first()
        list_parent_id = list()
        # we should not fall on the source transformer again when getting all parents of the target transformer
        list_parent_id.append(source_transformer.id)
        while target_transformer is not None and target_transformer.id not in list_parent_id:
            list_parent_id.append(target_transformer.id)
            target_transformer = target_transformer.get_parent()
        if target_transformer is not None and target_transformer.id in list_parent_id:
            return True
        return False

    def create(self, *args, **kwargs):
        if self.consume_from_resource_group is not None and self.factor is None:
            self.factor = 1
        super(Transformer, self).save(*args, **kwargs)

    def save(self, *args, **kwargs):
        try:
            if (self.consume_from_resource_group is not None and self.consume_from_attribute_definition is not None) \
                    and self.factor is None:
                self.factor = 1
        except ValueError:  # when saving from a form we have no id
            pass
        super(Transformer, self).save(*args, **kwargs)

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

    def set_factor(self, new_factor):
        self.factor = new_factor
        self.save()
        self.notify_parent()

    def calculate_total_produced(self):
        """
        Calculate the sum of all source attribute
        """
        total_produced = 0
        all_resource_att = ResourceAttribute.objects.filter(
            resource_id__in=self.resource_group.resources.all().values("id"),
            attribute_definition=self.attribute_definition)
        for attribute in all_resource_att:
            total_produced += attribute.value
        self.total_produced = total_produced
        self.save()
        return self.total_produced

    def calculate_total_consumed(self):
        """
        Calculate the sum of all destination attribute
        """
        total_consumed = 0
        transformers = Transformer.objects.filter(consume_from_attribute_definition=self.attribute_definition,
                                                  consume_from_resource_group=self.resource_group)
        for transformer in transformers:
            factor = transformer.factor if transformer.factor is not None else 1
            total_consumed += transformer.total_produced / factor
        self.total_consumed = total_consumed
        self.save()
        return self.total_consumed

    def get_parent(self):
        if self.consume_from_resource_group is not None and self.consume_from_resource_group.id is not None:
            return self.consume_from_resource_group.transformers \
                .filter(attribute_definition=self.consume_from_attribute_definition).first()
        return None

    def notify_parent(self):
        if self.get_parent() is not None:
            self.get_parent().calculate_total_consumed()

    def change_consumer(self, resource_group, attribute):
        # get old transformer
        old_parent = self.get_parent()
        # update the new parent
        self.consume_from_resource_group = resource_group
        self.consume_from_attribute_definition = attribute
        self.save()
        self.notify_parent()
        # update old parent
        if old_parent:
            old_parent.calculate_total_consumed()

    def delete(self, using=None, keep_parents=False):
        # delete all resource attribute from the resource group
        for resource in self.resource_group.resources.all():
            for attribute_value in resource.resource_attributes.filter(attribute_definition=self.attribute_definition):
                attribute_value.delete()

        # delete parent transformer that point to this one
        for children_transformer in Transformer.objects.filter(consume_from_resource_group=self.resource_group,
                                                               consume_from_attribute_definition=self.attribute_definition):
            children_transformer.consume_from_resource_group = None
            children_transformer.consume_from_attribute_definition = None
            children_transformer.save()
        super(Transformer, self).delete()
