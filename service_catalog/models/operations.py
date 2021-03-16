import copy

from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
from jsonfield import JSONField

from service_catalog.models import JobTemplate
from service_catalog.models import Service


class OperationType(models.TextChoices):
    CREATE = 'CREATE', _('Create')
    UPDATE = 'UPDATE', _('Update')
    DELETE = 'DELETE', _('Delete')


class Operation(models.Model):

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True, null=True)
    type = models.CharField(
        max_length=10,
        choices=OperationType.choices,
        default=OperationType.CREATE,
    )
    enabled_survey_fields = JSONField(blank=True, null=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    job_template = models.ForeignKey(JobTemplate, on_delete=models.CASCADE)
    auto_accept = models.BooleanField(default=False)
    auto_process = models.BooleanField(default=False)

    def update_survey(self):
        new_end_user_survey = dict()
        old_enabled_survey_fields = copy.copy(self.enabled_survey_fields)
        for survey_field in self.job_template.survey["spec"]:
            field_id = survey_field["variable"]
            if field_id not in old_enabled_survey_fields:
                new_end_user_survey[field_id] = True
            else:
                new_end_user_survey[field_id] = old_enabled_survey_fields[field_id]
        self.enabled_survey_fields = new_end_user_survey
        self.save()

    @classmethod
    def add_job_template_survey_as_default_survey(cls, sender, instance, created, *args, **kwargs):
        if created:
            # copy the default survey and add a flag 'is_visible'
            default_survey = instance.job_template.survey
            end_user_survey = dict()
            for survey_field in default_survey["spec"]:
                end_user_survey[survey_field["variable"]] = True
            instance.enabled_survey_fields = end_user_survey
            instance.save()

    @classmethod
    def update_survey_after_job_template_update(cls, job_template):
        # get all operation that use the target job template
        operations = Operation.objects.filter(job_template=job_template)
        for operation in operations:
            operation.update_survey()


post_save.connect(Operation.add_job_template_survey_as_default_survey, sender=Operation)
