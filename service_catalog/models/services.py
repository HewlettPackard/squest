from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from service_catalog.models import OperationType


class Service(models.Model):
    name = models.CharField(verbose_name="Service name", max_length=100)
    description = models.CharField(max_length=500, blank=True)
    image = models.ImageField(upload_to='service_image', blank=True)
    billing_group_id = models.IntegerField(null=True, default=None)
    billing_group_is_shown = models.BooleanField(default=False)
    billing_group_is_selectable = models.BooleanField(default=False)
    billing_groups_are_restricted = models.BooleanField(default=True)
    enabled = models.BooleanField(default=False, blank=True)

    def can_be_enabled(self):
        operation_create = self.operations.filter(type=OperationType.CREATE, enabled=True)
        if operation_create.count() == 1:
            if operation_create.first().job_template is not None:
                return True
        return False

    def __str__(self):
        return self.name

    def clean(self):
        if self.enabled and not self.can_be_enabled():
            raise ValidationError({'enabled': _("Service cannot be enabled if its 'CREATE' operation is not valid.")})


@receiver(pre_save, sender=Service)
def service_pre_save(sender, instance, **kwargs):
    if instance.enabled and not instance.can_be_enabled():
        instance.enabled = False
        instance.save()
