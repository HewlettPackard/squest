import logging

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from service_catalog.models import Service, JobTemplate

logger = logging.getLogger(__name__)


class HookModel(models.TextChoices):
    Request = 'Request', _('Request')
    Instance = 'Instance', _('Instance')


class ServiceStateHook(models.Model):
    instance = models.ForeignKey(Service,
                                 on_delete=models.CASCADE,
                                 related_name='instances',
                                 related_query_name='instance',
                                 null=True)
    model = models.CharField(max_length=100, choices=HookModel.choices)
    state = models.CharField(max_length=100)
    job_template = models.ForeignKey(JobTemplate, on_delete=models.CASCADE)
    extra_vars = models.JSONField(default=dict, blank=True)

    def clean(self):
        if self.extra_vars is None:
            raise ValidationError({'extra_vars': _("Please enter a valid JSON. Empty value is {} for JSON.")})


class GlobalHook(models.Model):
    name = models.CharField(unique=True, max_length=100)
    model = models.CharField(max_length=100, choices=HookModel.choices)
    state = models.CharField(max_length=100)
    job_template = models.ForeignKey(JobTemplate, on_delete=models.CASCADE)
    extra_vars = models.JSONField(default=dict, blank=True)

    def clean(self):
        if self.extra_vars is None:
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
        from service_catalog.serializers.instance_serializer import InstanceReadSerializer
        from service_catalog.serializers.request_serializers import RequestSerializer
        from service_catalog.models import Instance, Request
        if global_hook_set:
            # serialize the instance
            serialized_data = dict()
            if isinstance(instance, Instance):
                serialized_data = InstanceReadSerializer(instance).data
            if isinstance(instance, Request):
                serialized_data = RequestSerializer(instance).data
            for global_hook in global_hook_set.all():
                extra_vars = global_hook.extra_vars
                extra_vars["squest"] = serialized_data
                global_hook.job_template.execute(extra_vars=extra_vars)
