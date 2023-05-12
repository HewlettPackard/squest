from django.db import models


class AttributeDefinition(models.Model):
    name = models.CharField(max_length=100,
                            blank=False)

    description = models.CharField(max_length=100, default='', null=True, blank=True)

    def delete(self, using=None, keep_parents=False):
        # remove the pointer to this attribute in all transformer that were using it
        from resource_tracker_v2.models import Transformer
        for transformer in Transformer.objects.filter(consume_from_attribute_definition=self):
            transformer.consume_from_resource_group = None
            transformer.consume_from_attribute_definition = None
            transformer.save()

        super(AttributeDefinition, self).delete()
