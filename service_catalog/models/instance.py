import logging
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django_fsm import FSMField, transition, post_transition
from profiles.models import BillingGroup
from profiles.models.role_manager import RoleManager
from . import Service, InstanceState
from .state_hooks import HookManager

logger = logging.getLogger(__name__)


class Instance(RoleManager):
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
        return f"{self.name} (#{self.id})"

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

    @transition(field=state, source=[InstanceState.AVAILABLE, InstanceState.UPDATE_FAILED],
                target=InstanceState.UPDATING)
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
        self.delete_linked_resources()

    @transition(field=state, source=InstanceState.DELETED, target=InstanceState.ARCHIVED)
    def archive(self):
        pass

    def reset_to_last_stable_state(self):
        if self.state == InstanceState.PROVISION_FAILED:
            self.state = InstanceState.PENDING
        if self.state in [InstanceState.UPDATE_FAILED, InstanceState.DELETE_FAILED]:
            self.state = InstanceState.AVAILABLE

    def add_user_in_role(self, user, role_name):
        super(Instance, self).add_user_in_role(user, role_name)
        for request in self.request_set.all():
            request.add_user_in_role(user, role_name)

    def get_roles_of_users(self):
        roles = super(Instance, self).get_roles_of_users()
        if self.spoc:
            roles[self.spoc.id].append("SPOC")
        return roles

    def remove_user_in_role(self, user, role_name=None):
        super(Instance, self).remove_user_in_role(user, role_name)
        for request in self.request_set.all():
            request.remove_user_in_role(user, role_name)

    def add_team_in_role(self, team, role_name):
        super(Instance, self).add_team_in_role(team, role_name)
        for request in self.request_set.all():
            request.add_team_in_role(team, role_name)

    def remove_team_in_role(self, team, role_name=None):
        super(Instance, self).remove_team_in_role(team, role_name)
        for request in self.request_set.all():
            request.remove_team_in_role(team, role_name)

    def assign_permission_to_spoc(self):
        if self.spoc:
            self.add_user_in_role(self.spoc, "Admin")

    def remove_permission_to_spoc(self):
        self.remove_user_in_role(self.spoc, "Admin")

    def delete_linked_resources(self):
        for resource in self.resources.all():
            if resource.is_deleted_on_instance_deletion:
                resource.delete()

    @classmethod
    def trigger_hook_handler(cls, sender, instance, name, source, target, *args, **kwargs):
        """
        Proxy method. Cannot be mocked for testing
        """
        HookManager.trigger_hook(sender, instance, name, source, target, *args, **kwargs)

    @classmethod
    def on_create_call_hook_manager(cls, sender, instance, created, *args, **kwargs):
        if created:
            HookManager.trigger_hook(sender=sender, instance=instance, name="create", source="create",
                                     target=InstanceState.PENDING, *args, **kwargs)


post_transition.connect(Instance.trigger_hook_handler, sender=Instance)
post_save.connect(Instance.on_create_call_hook_manager, sender=Instance)


@receiver(pre_save, sender=Instance)
def pre_save(sender, instance, **kwargs):
    instance._old_billing_group = None
    instance._need_update = False
    if instance.id:
        old_instance = sender.objects.get(id=instance.id)
        if old_instance.billing_group != instance.billing_group:
            instance._old_billing_group = old_instance.billing_group
            instance._need_update = True
        if old_instance.spoc != instance.spoc:
            old_instance.remove_permission_to_spoc()
            instance.assign_permission_to_spoc()


@receiver(post_save, sender=Instance)
def post_save(sender, instance, created, **kwargs):
    if created:
        instance.assign_permission_to_spoc()
        update_quota(instance.billing_group)
    if instance._need_update:
        update_quota(instance._old_billing_group)
        update_quota(instance.billing_group)


@receiver(pre_delete, sender=Instance)
def pre_delete(sender, instance, **kwargs):
    instance.remove_all_bindings()
    instance.delete_linked_resources()


def update_quota(billing_group):
    if billing_group is not None:
        for binding in billing_group.quota_bindings.all():
            binding.update_consumed()
