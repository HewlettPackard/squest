import logging

from django.core.exceptions import ValidationError
from django.db.models import CharField, ImageField, BooleanField, ForeignKey, SET_NULL, JSONField, ManyToManyField
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from Squest.utils.squest_model import SquestModel
from profiles.models import Permission
from service_catalog.models.operation_type import OperationType

logger = logging.getLogger(__name__)

class Service(SquestModel):
    class Meta:
        permissions = [
            ("request_on_service", "Can request operation on service"),
            ("admin_request_on_service", "Can request an admin operation on service"),
        ]
        default_permissions = ('add', 'change', 'delete', 'view', 'list')

    name = CharField(verbose_name="Service name", max_length=100)
    description = CharField(max_length=500, blank=True)
    external_support_url = CharField(max_length=2000, blank=True)
    image = ImageField(upload_to='service_image', blank=True)
    enabled = BooleanField(default=False, blank=True)
    parent_portfolio = ForeignKey(
        "service_catalog.Portfolio",
        blank=True,
        null=True,
        on_delete=SET_NULL,
        related_name="service_list",
        related_query_name="service_list",
    )
    extra_vars = JSONField(default=dict, blank=True)
    description_doc = ForeignKey('service_catalog.Doc', blank=True, null=True, on_delete=SET_NULL, verbose_name='Description documentation')
    attribute_definitions = ManyToManyField(
        'resource_tracker_v2.AttributeDefinition',
        related_name="services",
        blank=True,
        help_text="List of attributes linked to the service, they could be used on operation fields.",
    )

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
            raise ValidationError({'enabled': _("At least one 'CREATE' operation with a valid job template is required "
                                                "to enable the service")})

        if self.extra_vars is None or not isinstance(self.extra_vars, dict):
            raise ValidationError({'extra_vars': _("Please enter a valid JSON. Empty value is {} for JSON.")})

    def bulk_set_permission_on_operation(self, target_permission):
        from service_catalog.models import Operation
        logger.debug(f"Bulk edit permission on service {self.name} to permission {target_permission}")
        # check if all permission are already set to the target perm
        all_permission_current_service = Permission.objects.filter(operation__service=self).distinct()
        # if the target perm is already the one used we do nothing
        if all_permission_current_service.count() == 1:
            if all_permission_current_service.first() == target_permission:
                return
        Operation.objects.filter(service=self).update(permission=target_permission)


@receiver(pre_save, sender=Service)
def service_pre_save(sender, instance, **kwargs):
    if instance.id:
        if not instance.enabled:
            instance.operations.filter(type=OperationType.CREATE).update(**{"enabled": False})
        if instance.enabled and not instance.can_be_enabled():
            instance.enabled = False
            instance.save()