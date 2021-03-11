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
    survey = JSONField(blank=True, null=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    job_template = models.ForeignKey(JobTemplate, on_delete=models.CASCADE)

    @classmethod
    def add_job_template_survey_as_default_survey(cls, sender, instance, created, *args, **kwargs):
        if created:
            # copy the default survey and add a flag 'is_visible'
            default_survey = instance.job_template.survey
            end_user_survey = dict()
            for survey_field in default_survey["spec"]:
                end_user_survey[survey_field["variable"]] = True
            instance.survey = end_user_survey
            instance.save()


post_save.connect(Operation.add_job_template_survey_as_default_survey, sender=Operation)
