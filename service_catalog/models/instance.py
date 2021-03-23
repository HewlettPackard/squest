from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import User, Permission
from django.db import models
from django_fsm import FSMField, transition

from . import Service


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

    @transition(field=state, source=[InstanceState.PENDING, InstanceState.PROVISION_FAILED],
                target=InstanceState.PROVISIONING)
    def provisioning(self):
        pass

    @transition(field=state, source=InstanceState.PROVISIONING, target=InstanceState.PROVISION_FAILED)
    def provisioning_has_failed(self):
        pass

    @transition(field=state, source=[InstanceState.PROVISIONING, InstanceState.UPDATING],
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


class UserPermissionOnInstance(models.Model):
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        db_table = 'user_permission_on_instance'
        unique_together = ('instance', 'user')
