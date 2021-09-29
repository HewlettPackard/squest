import logging
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_fsm import FSMField, transition, post_transition
from guardian.models import UserObjectPermission
from profiles.models import BillingGroup
from . import Service, InstanceState
from .state_hooks import HookManager
logger = logging.getLogger(__name__)


class Instance(models.Model):
    name = models.CharField(verbose_name="Instance name", max_length=100)
    spec = models.JSONField(default=dict, blank=True)
    service = models.ForeignKey(Service, blank=True, null=True, on_delete=models.SET_NULL)
    spoc = models.ForeignKey(User, null=True, help_text='Single Point Of Contact', verbose_name="SPOC",
                             on_delete=models.SET_NULL)
    state = FSMField(default=InstanceState.PENDING)
    billing_group = models.ForeignKey(
        BillingGroup,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='instances',
        related_query_name='instance'
    )

    def __str__(self):
        return f"{self.id}-{self.name}"

    def clean(self):
        if self.spec is None:
            raise ValidationError({'spec': _("Please enter a valid JSON. Empty value is {} for JSON.")})

    def opened_support_count(self):
        from .support import SupportState
        return self.supports.filter(state=SupportState.OPENED).count()

    @transition(field=state, source=[InstanceState.PENDING, InstanceState.PROVISION_FAILED],
                target=InstanceState.PROVISIONING)
    def provisioning(self):
        pass

    @transition(field=state, source=InstanceState.PROVISIONING, target=InstanceState.PROVISION_FAILED)
    def provisioning_has_failed(self):
        pass

    @transition(field=state, source=[InstanceState.PROVISION_FAILED, InstanceState.DELETE_FAILED,
                                     InstanceState.UPDATE_FAILED,
                                     InstanceState.PROVISIONING, InstanceState.UPDATING],
                target=InstanceState.AVAILABLE)
    def available(self):
        pass

    @transition(field=state, source=InstanceState.AVAILABLE, target=InstanceState.UPDATING)
    def updating(self):
        pass

    @transition(field=state, source=InstanceState.UPDATING, target=InstanceState.UPDATE_FAILED)
    def update_has_failed(self):
        pass

    @transition(field=state, source=InstanceState.UPDATE_FAILED, target=InstanceState.UPDATING)
    def retry_update(self):
        pass

    @transition(field=state, source=[InstanceState.AVAILABLE, InstanceState.DELETE_FAILED],
                target=InstanceState.DELETING)
    def deleting(self):
        pass

    @transition(field=state, source=InstanceState.DELETING, target=InstanceState.DELETE_FAILED)
    def delete_has_failed(self):
        pass

    @transition(field=state, source=InstanceState.DELETING, target=InstanceState.DELETED)
    def deleted(self):
        pass

    @transition(field=state, source=InstanceState.DELETED, target=InstanceState.ARCHIVED)
    def archive(self):
        pass

    def reset_to_last_stable_state(self):
        if self.state == InstanceState.PROVISION_FAILED:
            self.state = InstanceState.PENDING
        if self.state in [InstanceState.UPDATE_FAILED, InstanceState.DELETE_FAILED]:
            self.state = InstanceState.AVAILABLE


post_transition.connect(HookManager.trigger_hook_handler, sender=Instance)


@receiver(post_save, sender=Instance)
def give_permissions_after_creation(sender, instance, created, **kwargs):
    if created:
        UserObjectPermission.objects.assign_perm('change_instance', instance.spoc, obj=instance)
        UserObjectPermission.objects.assign_perm('view_instance', instance.spoc, obj=instance)
