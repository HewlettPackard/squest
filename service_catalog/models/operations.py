from django.db import models
from django.utils.translation import gettext_lazy as _

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
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    job_template = models.ForeignKey(JobTemplate, on_delete=models.CASCADE)
