import logging

from django.db import models
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMField, transition, post_transition

from profiles.models import BillingGroup
from . import Service
from .state_hooks import HookManager

logger = logging.getLogger(__name__)


class InstanceState(models.TextChoices):
    PENDING = 'PENDING', _('PENDING')
    PROVISION_FAILED = 'PROVISION_FAILED', _('PROVISION_FAILED')
    PROVISIONING = 'PROVISIONING', _('PROVISIONING')
    UPDATING = 'UPDATING', _('UPDATING')
    UPDATE_FAILED = 'UPDATE_FAILED', _('UPDATE_FAILED')
    DELETING = 'DELETING', _('DELETING')
    DELETED = 'DELETED', _('DELETED')
    DELETE_FAILED = 'DELETE_FAILED', _('DELETE_FAILED')
    ARCHIVED = 'ARCHIVED', _('ARCHIVED')
    AVAILABLE = 'AVAILABLE', _('AVAILABLE')


class Instance(models.Model):
    name = models.CharField(max_length=100)
    spec = models.JSONField(default=dict)
    service = models.ForeignKey(Service, blank=True, null=True, on_delete=models.SET_NULL)
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
