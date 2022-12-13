import logging

from django.db.models import TextChoices, Model, ForeignKey, CASCADE, CharField, JSONField, SET_NULL
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from service_catalog.models.services import Service
from service_catalog.models.job_templates import JobTemplate
from service_catalog.models.operations import Operation

logger = logging.getLogger(__name__)


class HookModel(TextChoices):
    Request = 'Request', _('Request')
    Instance = 'Instance', _('Instance')


class ServiceStateHook(Model):
    instance = ForeignKey(Service,
                                 on_delete=CASCADE,
                                 related_name='instances',
                                 related_query_name='instance',
                                 null=True)
    model = CharField(max_length=100, choices=HookModel.choices)
    state = CharField(max_length=100)
    job_template = ForeignKey(JobTemplate, on_delete=CASCADE)
    extra_vars = JSONField(default=dict, blank=True)

    def clean(self):
        if self.extra_vars is None or not isinstance(self.extra_vars, dict):
            raise ValidationError({'extra_vars': _("Please enter a valid JSON. Empty value is {} for JSON.")})


class GlobalHook(Model):
    name = CharField(unique=True, max_length=100)
    model = CharField(max_length=100, choices=HookModel.choices)
    state = CharField(max_length=100)
    service = ForeignKey(Service, on_delete=SET_NULL, null=True, blank=True, default=None)
    operation = ForeignKey(Operation, on_delete=SET_NULL, null=True, blank=True, default=None)
    job_template = ForeignKey(JobTemplate, on_delete=CASCADE)
    extra_vars = JSONField(default=dict, blank=True)

    def clean(self):
        if self.operation and not self.service:
            raise ValidationError({'service': _("Service cannot be null if operation is set.")})
        if self.service and self.operation and not self.service.operations.filter(id=self.operation.id).exists():
            raise ValidationError({'operation': _(f"Operation must be in the service({','.join(operation.name for operation in self.service.operations.all())}).")})
        if self.extra_vars is None or not isinstance(self.extra_vars, dict):
            raise ValidationError({'extra_vars': _("Please enter a valid JSON. Empty value is {} for JSON.")})


class HookManager(object):

    @classmethod
    def trigger_hook(cls, sender, instance, name, source, target, *args, **kwargs):
        """
        Method called when Instance or Request change state
        :param sender: Class that call the signal (Instance or Request)
        :param instance: Instance object
        :param name: name of the FSM method
        :param source: source state
        :param target: target state (current)
        :return:
        """
        logger.debug(f"[HookManager] trigger_hook executed with "
                     f"sender model '{sender.__name__}', "
                     f"instance ID'{instance.id}', "
                     f"transition name '{name}', "
                     f"source '{source}', "
                     f"target '{target}'")
        # check if global hooks exist for this object sender model and state
        global_hook_set = GlobalHook.objects.filter(model=sender.__name__, state=target)
        from service_catalog.api.serializers import InstanceReadSerializer, AdminRequestSerializer
        from service_catalog.models import Instance, Request
        if global_hook_set:
            # serialize the instance
            serialized_data = dict()
            service = None
            operations = list()
            from django.conf import settings
            extra_vars = {
                "squest_host": settings.SQUEST_HOST,
                "squest": dict()
            }
            if isinstance(instance, Instance):
                service = instance.service
                operations = instance.service.operations.all()
                serialized_data = dict(InstanceReadSerializer(instance).data)
                extra_vars["squest"]["instance"] = serialized_data
            if isinstance(instance, Request):
                service = instance.instance.service
                operations = [instance.operation]
                serialized_data = dict(AdminRequestSerializer(instance).data)
                extra_vars["squest"]["request"] = serialized_data
            for global_hook in global_hook_set.all():
                if global_hook.service is None or service == global_hook.service:
                    if global_hook.operation is None or global_hook.operation in operations:
                        extra_vars.update(global_hook.extra_vars)
                        global_hook.job_template.execute(extra_vars=extra_vars)
