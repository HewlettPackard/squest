import logging

from django.db.models import Model, CharField, BooleanField, ForeignKey, CASCADE
from django.db.models.signals import pre_save
from django.dispatch import receiver

from service_catalog.models import Operation

logger = logging.getLogger(__name__)


class TowerSurveyField(Model):
    name = CharField(null=False, blank=False, max_length=200, verbose_name="Field name")
    enabled = BooleanField(default=True, null=False, blank=False)
    default = CharField(null=True, blank=True, max_length=200, verbose_name="Default value")
    operation = ForeignKey(Operation,
                           on_delete=CASCADE,
                           related_name="tower_survey_fields",
                           related_query_name="tower_survey_field")
    validators = CharField(null=True, blank=True, max_length=200, verbose_name="Field validators")

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('operation', 'name',)


@receiver(pre_save, sender=TowerSurveyField)
def on_change(sender, instance: TowerSurveyField, **kwargs):
    if instance.id is not None:
        previous = TowerSurveyField.objects.get(id=instance.id)
        if previous.enabled != instance.enabled:
            # update all request that use this tower field survey. Move filled fields between user and admin survey
            for request in instance.operation.request_set.all():
                if instance.name in request.admin_fill_in_survey.keys() and instance.enabled:
                    old = request.admin_fill_in_survey.pop(instance.name)
                    request.fill_in_survey[instance.name] = old
                elif instance.name in request.fill_in_survey.keys() and not instance.enabled:
                    old = request.fill_in_survey.pop(instance.name)
                    request.admin_fill_in_survey[instance.name] = old
                else:
                    logger.warning("[set_field_in_survey] field has not changed")
                request.save()
