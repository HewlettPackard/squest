import logging
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import CharField, JSONField, ForeignKey, SET_NULL, DateTimeField, SET_DEFAULT, ManyToManyField
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django_fsm import FSMField, transition, post_transition

from Squest.utils.ansible_when import AnsibleWhen
from Squest.utils.squest_model import SquestModel
from profiles.models.scope import Scope
from service_catalog.models.services import Service
from service_catalog.models.instance_state import InstanceState
from service_catalog.models.state_hooks import HookManager

logger = logging.getLogger(__name__)


def get_default_org():
    from profiles.models import Organization
    return Organization.objects.get_or_create(name="Default org")[0].id


class Instance(SquestModel):
    name = CharField(verbose_name="Instance name", max_length=100)
    spec = JSONField(default=dict, blank=True, verbose_name="Admin spec")
    user_spec = JSONField(default=dict, blank=True, verbose_name="User spec")
    service = ForeignKey(Service, blank=True, null=True, on_delete=SET_NULL)
    requester = ForeignKey(User, null=True, help_text='Initial request', verbose_name="Requester", on_delete=SET_NULL)
    scopes = ManyToManyField(
        Scope,
        blank=True,
        related_name='instances',
        related_query_name='instance'
    )
    state = FSMField(default=InstanceState.PENDING)
    date_available = DateTimeField(null=True, blank=True)

    @classmethod
    def get_queryset_for_user(cls, user, perm):
        from profiles.models import Team
        qs = super().get_queryset_for_user(user, perm)
        if qs.exists():
            return qs
        app_label, codename = perm.split(".")
        return Instance.objects.filter(scope__rbac__user=user,
                                       scope__rbac__role__permissions__codename=codename,
                                       scope__rbac__role__permissions__content_type__app_label=app_label) | \
               Instance.objects.filter(scope__in=Team.objects.filter(org__rbac__user=user),
                                       scope__rbac__role__permissions__codename=codename,
                                       scope__rbac__role__permissions__content_type__app_label=app_label)

    def get_scopes(self):
        return self.scope.get_scopes()

    def __str__(self):
        return f"{self.name} (#{self.id})"

    @property
    def docs(self):
        filtered_doc = list()
        for doc in self.service.docs.all():
            context = {
                "instance": self
            }
            if not doc.when or (doc.when and AnsibleWhen.when_render(context=context, when_string=doc.when)):
                filtered_doc.append(doc)
        return filtered_doc

    def clean(self):
        if self.user_spec is None:
            raise ValidationError({'user_spec': _("Please enter a valid JSON. Empty value is {} for JSON.")})
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

    def delete_linked_resources(self):
        self.resources.filter(is_deleted_on_instance_deletion=True).delete()

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


@receiver(pre_delete, sender=Instance)
def pre_delete(sender, instance, **kwargs):
    instance.delete_linked_resources()
