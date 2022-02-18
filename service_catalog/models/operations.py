from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


from service_catalog.models import JobTemplate, OperationType
from service_catalog.models import Service


class Operation(models.Model):
    name = models.CharField(max_length=100, verbose_name="Operation name")
    description = models.CharField(max_length=500, blank=True, null=True)
    type = models.CharField(
        max_length=10,
        choices=OperationType.choices,
        default=OperationType.CREATE,
        verbose_name="Operation type"
    )
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="operations",
                                related_query_name="operation")
    job_template = models.ForeignKey(JobTemplate, null=True, on_delete=models.SET_NULL)
    auto_accept = models.BooleanField(default=False)
    auto_process = models.BooleanField(default=False)
    process_timeout_second = models.IntegerField(default=60, verbose_name="Process timeout (s)")

    def clean(self):
        if hasattr(self, 'service'):
            if self.type == OperationType.CREATE:
                if self.service:
                    if self.service.operations.filter(type=OperationType.CREATE).count() != 0:
                        if self.service.operations.filter(type=OperationType.CREATE).first().id != self.id:
                            raise ValidationError({'service': _("A service can have only one 'CREATE' operation")})

    def update_survey(self):
        if self.job_template is not None:
            spec_list = self.job_template.survey.get("spec", [])
            list_of_field_to_have = [survey_spec["variable"] for survey_spec in spec_list]
            list_current_field = [tower_field.name for tower_field in self.tower_survey_fields.all()]
            to_add = list(set(list_of_field_to_have) - set(list_current_field))
            to_remove = list(set(list_current_field) - set(list_of_field_to_have))

            from service_catalog.models.tower_survey_field import TowerSurveyField
            for field_name in to_add:
                TowerSurveyField.objects.create(name=field_name, enabled=True, operation=self)
            for field_name in to_remove:
                TowerSurveyField.objects.get(name=field_name, operation=self).delete()

    def switch_tower_fields_enable_from_dict(self, dict_of_field):
        for key, enabled in dict_of_field.items():
            field = self.tower_survey_fields.get(name=key)
            field.enabled = enabled
            field.save()

    @classmethod
    def add_job_template_survey_as_default_survey(cls, sender, instance, created, *args, **kwargs):
        from service_catalog.models.tower_survey_field import TowerSurveyField
        if created:
            # copy the default survey and add a flag 'is_visible'
            default_survey = instance.job_template.survey
            if "spec" in default_survey:
                for survey_field in default_survey["spec"]:
                    TowerSurveyField.objects.create(name=survey_field["variable"], enabled=True, operation=instance)

    @classmethod
    def update_survey_after_job_template_update(cls, job_template):
        # get all operation that use the target job template
        operations = Operation.objects.filter(job_template=job_template)
        for operation in operations:
            operation.update_survey()


post_save.connect(Operation.add_job_template_survey_as_default_survey, sender=Operation)


@receiver(pre_save, sender=Operation)
def on_change(sender, instance: Operation, **kwargs):
    # disable the service if no more job template linked to a create operation
    if instance.job_template is None and instance.type == OperationType.CREATE:
        instance.service.enabled = False
        instance.service.save()
    if instance.id is not None:
        previous = Operation.objects.get(id=instance.id)
        if previous.job_template != instance.job_template:
            instance.update_survey()
