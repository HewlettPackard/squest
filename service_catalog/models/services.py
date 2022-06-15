from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.db.models import Model, CharField, ImageField, IntegerField, BooleanField
from django.db.models.signals import pre_save
from django.dispatch import receiver

from service_catalog.models import OperationType


class Service(Model):
    name = CharField(verbose_name="Service name", max_length=100)
    description = CharField(max_length=500, blank=True)
    image = ImageField(upload_to='service_image', blank=True)
    billing_group_id = IntegerField(null=True, default=None)
    billing_group_is_shown = BooleanField(default=False)
    billing_group_is_selectable = BooleanField(default=False)
    billing_groups_are_restricted = BooleanField(default=True)
    enabled = BooleanField(default=False, blank=True)

    def can_be_enabled(self):
        operation_create_list = self.operations.filter(type=OperationType.CREATE, enabled=True)
        if operation_create_list.exists():
            for operation in operation_create_list:
                if operation.job_template is not None and operation.enabled == True:
                    return True
        return False

    def __str__(self):
        return self.name

    def clean(self):
        if self.enabled and not self.can_be_enabled():
            raise ValidationError({'enabled': _("Service cannot be enabled if at least one 'CREATE' operation is not "
                                                "valid.")})


@receiver(pre_save, sender=Service)
def service_pre_save(sender, instance, **kwargs):
    if not instance.enabled:
        instance.operations.filter(type=OperationType.CREATE).update(**{"enabled": False})
    if instance.enabled and not instance.can_be_enabled():
        instance.enabled = False
        instance.save()
