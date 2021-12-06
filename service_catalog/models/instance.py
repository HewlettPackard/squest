import logging

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django_fsm import FSMField, transition, post_transition
from profiles.models import BillingGroup, Role, UserRoleBinding, Team, TeamRoleBinding
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

    def __init__(self, *args, **kwargs):
        super(Instance, self).__init__(*args, **kwargs)
        self.roles = Role.objects.filter(content_type=ContentType.objects.get_for_model(Instance))

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
        pass

    @transition(field=state, source=InstanceState.DELETED, target=InstanceState.ARCHIVED)
    def archive(self):
        pass

    def reset_to_last_stable_state(self):
        if self.state == InstanceState.PROVISION_FAILED:
            self.state = InstanceState.PENDING
        if self.state in [InstanceState.UPDATE_FAILED, InstanceState.DELETE_FAILED]:
            self.state = InstanceState.AVAILABLE

    def add_user_in_role(self, user, role_name):
        UserRoleBinding.objects.get_or_create(
            user=user,
            content_type=ContentType.objects.get_for_model(Instance),
            object_id=self.id,
            role=self.roles.get(name=role_name)
        )

    def get_users_in_role(self, role_name):
        bindings = UserRoleBinding.objects.filter(role=self.roles.get(name=role_name), object_id=self.id)
        return User.objects.filter(id__in=[binding.user.id for binding in bindings])

    def get_all_users(self):
        bindings = UserRoleBinding.objects.filter(role__in=self.roles, object_id=self.id)
        return User.objects.filter(id__in=[binding.user.id for binding in bindings])

    def get_roles_of_users(self):
        roles = dict()
        for user in self.get_all_users():
            roles[user.id] = [binding.role.name for binding in UserRoleBinding.objects.filter(
                user=user,
                content_type=ContentType.objects.get_for_model(Instance),
                object_id=self.id)]
        roles[self.spoc.id].append("SPOC")
        return roles

    def remove_user(self, user, role_name=None):
        if role_name:
            bindings = UserRoleBinding.objects.filter(user=user,
                                                      content_type=ContentType.objects.get_for_model(Instance),
                                                      object_id=self.id, role__name=role_name)
        else:
            bindings = UserRoleBinding.objects.filter(user=user,
                                                      content_type=ContentType.objects.get_for_model(Instance),
                                                      object_id=self.id)
        for binding in bindings:
            binding.delete()

    def add_team_in_role(self, team, role_name):
        TeamRoleBinding.objects.get_or_create(
            team=team,
            content_type=ContentType.objects.get_for_model(Instance),
            object_id=self.id,
            role=self.roles.get(name=role_name)
        )

    def get_teams_in_role(self, role_name):
        bindings = TeamRoleBinding.objects.filter(role=self.roles.get(name=role_name), object_id=self.id)
        return Team.objects.filter(id__in=[binding.team.id for binding in bindings])

    def get_all_teams(self):
        bindings = TeamRoleBinding.objects.filter(role__in=self.roles, object_id=self.id)
        return Team.objects.filter(id__in=[binding.team.id for binding in bindings])

    def get_roles_of_teams(self):
        roles = dict()
        for team in self.get_all_teams():
            roles[team.id] = [binding.role.name for binding in TeamRoleBinding.objects.filter(
                team=team,
                content_type=ContentType.objects.get_for_model(Instance),
                object_id=self.id)]
        return roles

    def remove_team(self, team):
        bindings = TeamRoleBinding.objects.filter(team=team,
                                                  content_type=ContentType.objects.get_for_model(Instance),
                                                  object_id=self.id)
        for binding in bindings:
            binding.delete()


post_transition.connect(HookManager.trigger_hook_handler, sender=Instance)


@receiver(pre_save, sender=Instance)
def change_spoc(sender, instance, **kwargs):
    if instance.id:
        old_instance = sender.objects.get(id=instance.id)
        if old_instance.spoc != instance.spoc:
            remove_permission_to_spoc(old_instance)
            assign_permission_to_spoc(instance)


@receiver(post_save, sender=Instance)
def give_permissions_after_creation(sender, instance, created, **kwargs):
    if created:
        assign_permission_to_spoc(instance)


def assign_permission_to_spoc(instance):
    instance.add_user_in_role(instance.spoc, "Admin")


def remove_permission_to_spoc(instance):
    instance.remove_user(instance.spoc, "Admin")
