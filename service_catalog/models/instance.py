from django.contrib.auth.models import User, Permission
from django.db import models
from django_fsm import FSMField, transition

from . import Service


class Instance(models.Model):
    name = models.CharField(max_length=100)
    spec = models.JSONField(default=dict)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    state = FSMField(default='PENDING')

    @transition(field=state, source=['PENDING', 'PROVISION_FAILED'], target='PROVISIONING')
    def provisioning(self):
        pass

    @transition(field=state, source='PROVISIONING', target='PROVISION_FAILED')
    def provisioning_has_failed(self):
        pass

    @transition(field=state, source=['PROVISIONING', 'UPDATING'], target='AVAILABLE')
    def available(self):
        pass

    @transition(field=state, source='AVAILABLE', target='UPDATING')
    def update(self):
        pass

    @transition(field=state, source='UPDATING', target='UPDATE_FAILED')
    def update_has_failed(self):
        pass

    @transition(field=state, source='UPDATE_FAILED', target='UPDATING')
    def retry_update(self):
        pass

    @transition(field=state, source=['AVAILABLE', 'DELETE_FAILED'], target='DELETING')
    def deleting(self):
        pass

    @transition(field=state, source='DELETING', target='DELETE_FAILED')
    def delete_has_failed(self):
        pass

    @transition(field=state, source='DELETING', target='DELETED')
    def deleted(self):
        pass

    @transition(field=state, source='DELETED', target='ARCHIVED')
    def archive(self):
        pass


class UserPermissionOnInstance(models.Model):
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        db_table = 'user_permission_on_instance'
        unique_together = ('instance', 'user')
