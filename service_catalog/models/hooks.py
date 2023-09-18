import logging

from django.core.exceptions import ValidationError
from django.db.models import ForeignKey, CASCADE, CharField, JSONField, SET_NULL, IntegerField, ManyToManyField
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from Squest.utils.squest_model import SquestModel
from service_catalog.models import InstanceState, RequestState, Service
from service_catalog.models.job_templates import JobTemplate
from service_catalog.models.operations import Operation

logger = logging.getLogger(__name__)


class AbstractGlobalHook(SquestModel):
    class Meta(SquestModel.Meta):
        abstract = True

    name = CharField(unique=True, max_length=100)
    job_template = ForeignKey(JobTemplate, on_delete=CASCADE)
    extra_vars = JSONField(default=dict, blank=True)

    def clean(self):
        if self.extra_vars is None or not isinstance(self.extra_vars, dict):
            raise ValidationError({'extra_vars': _("Please enter a valid JSON. Empty value is {} for JSON.")})

    def __str__(self):
        return self.name


class InstanceHook(AbstractGlobalHook):
    state = IntegerField(choices=InstanceState.choices)
    services = ManyToManyField(Service,  blank=True, default=None)

    def get_absolute_url(self):
        return reverse_lazy("service_catalog:instancehook_list")


class RequestHook(AbstractGlobalHook):
    state = IntegerField(choices=RequestState.choices)
    operations = ManyToManyField(Operation, blank=True, default=None)

    def get_absolute_url(self):
        return reverse_lazy("service_catalog:requesthook_list")


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
        from service_catalog.api.serializers import InstanceReadSerializer, AdminRequestSerializer
        from service_catalog.models import Instance, Request
        logger.debug(f"[HookManager] trigger_hook executed with "
                     f"sender model '{sender.__name__}', "
                     f"instance ID'{instance.id}', "
                     f"transition name '{name}', "
                     f"source '{source}', "
                     f"target '{target}'")

        # serialize the instance
        from django.conf import settings
        # check if global hooks exist for this object sender model and state
        if sender.__name__ == "Instance":
            global_hook_set = InstanceHook.objects.filter(state=target)
            service = instance.service
            serialized_data = InstanceReadSerializer(instance).data
            for global_hook in global_hook_set.all():
                if global_hook.services.count() == 0 or service in global_hook.services.all():
                    extra_vars = {
                        "squest": {
                            "squest_host": settings.SQUEST_HOST,
                            "instance": serialized_data
                        }
                    }
                    extra_vars.update(global_hook.extra_vars)
                    global_hook.job_template.execute(extra_vars=extra_vars)

        elif sender.__name__ == "Request":
            global_hook_set = RequestHook.objects.filter(state=target)
            operation = instance.operation
            serialized_data = dict(AdminRequestSerializer(instance).data)
            for global_hook in global_hook_set.all():
                extra_vars = {
                    "squest": {
                        "squest_host": settings.SQUEST_HOST,
                        "request": serialized_data
                    }
                }
                if global_hook.operations.count() == 0 or operation in global_hook.operations.all():
                    extra_vars.update(global_hook.extra_vars)
                    global_hook.job_template.execute(extra_vars=extra_vars)
