import logging

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import CharField, JSONField, ForeignKey, DateTimeField, PROTECT, Q, \
    CASCADE
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django_fsm import transition, FSMIntegerField

from Squest.utils.ansible_when import AnsibleWhen
from Squest.utils.squest_model import SquestModel
from profiles.models.scope import Scope
from service_catalog.models.hooks import HookManager
from service_catalog.models.instance_state import InstanceState
from service_catalog.models.services import Service

logger = logging.getLogger(__name__)


class Instance(SquestModel):
    class Meta:
        ordering = ["-last_updated"]
        permissions = [
            ("archive_instance", "Can archive instance"),
            ("unarchive_instance", "Can unarchive instance"),
            ("request_on_instance", "Can request a day2 operation on instance"),
            ("admin_request_on_instance", "Can request an admin day2 operation on instance"),
            ("view_admin_spec_instance", "Can view admin spec on instance"),
            ("change_admin_spec_instance", "Can change admin spec on instance"),
        ]
        default_permissions = ('add', 'change', 'delete', 'view', 'list')


    name = CharField(verbose_name="Instance name", max_length=100)
    spec = JSONField(default=dict, blank=True, verbose_name="Admin spec")
    user_spec = JSONField(default=dict, blank=True, verbose_name="User spec")
    service = ForeignKey(Service, blank=True, null=True, on_delete=CASCADE)
    requester = ForeignKey(User, null=True, help_text='Initial requester', verbose_name="Owner", on_delete=PROTECT)

    quota_scope = ForeignKey(
        Scope,
        related_name="quota_instances",
        related_query_name="quota_instance",
        on_delete=PROTECT
    )
    state = FSMIntegerField(default=InstanceState.PENDING, choices=InstanceState.choices)
    date_available = DateTimeField(null=True, blank=True)

    @classmethod
    def get_q_filter(cls, user, perm):
        from profiles.models import Team
        app_label, codename = perm.split(".")

        from profiles.models import GlobalScope
        globalscope = GlobalScope.load()
        additional_q = Q()
        if globalscope.owner_permissions.filter(
                codename=codename,
                content_type__app_label=app_label
        ).exists():
            additional_q = Q(requester=user)

        return Q(
            # Quota scope
            ## Quota scope - Org - User
            quota_scope__rbac__user=user,
            quota_scope__rbac__role__permissions__codename=codename,
            quota_scope__rbac__role__permissions__content_type__app_label=app_label
        ) | Q(
            ## Quota scope - Org - Default roles
            quota_scope__rbac__user=user,
            quota_scope__roles__permissions__codename=codename,
            quota_scope__roles__permissions__content_type__app_label=app_label
        ) | Q(
            ## Quota scope - Team - User
            quota_scope__in=Team.objects.filter(
                org__rbac__user=user,
                org__rbac__role__permissions__codename=codename,
                org__rbac__role__permissions__content_type__app_label=app_label
            )
        ) | Q(
            ## Quota scope - Team - Default roles
            quota_scope__in=Team.objects.filter(
                org__rbac__user=user,
                org__roles__permissions__codename=codename,
                org__roles__permissions__content_type__app_label=app_label
            )
        ) | additional_q

    def who_has_perm(self, permission_str):
        users = super().who_has_perm(permission_str)
        ## Permission give via GlobalScope.owner_permission
        if self.requester:
            from profiles.models import GlobalScope
            app_label, codename = permission_str.split(".")
            if GlobalScope.load().owner_permissions.filter(codename=codename, content_type__app_label=app_label).exists():
                if self.requester:
                    users = users | User.objects.filter(pk=self.requester.pk).distinct()
        return users

    def get_scopes(self):
        return self.quota_scope.get_scopes()

    def is_owner(self, user):
        if self.requester:
            return self.requester == user

    def __str__(self):
        return f"{self.name} (#{self.id})"

    @property
    def docs(self):
        filtered_doc = list()
        from service_catalog.api.serializers import InstanceSerializer
        for doc in self.service.docs.all():
            context = {
                "instance": InstanceSerializer(self).data
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

    @transition(field=state, source=InstanceState.ARCHIVED, target=InstanceState.DELETED)
    def unarchive(self):
        pass

    @transition(field=state, source=InstanceState.PENDING, target=InstanceState.ABORTED)
    def abort(self):
        pass

    def reset_to_last_stable_state(self):
        if self.state == InstanceState.PROVISION_FAILED:
            self.state = InstanceState.PENDING
        if self.state in [InstanceState.UPDATE_FAILED, InstanceState.DELETE_FAILED]:
            self.state = InstanceState.AVAILABLE

    def delete_linked_resources(self):
        for resource in self.resources.filter(is_deleted_on_instance_deletion=True):
            resource.delete()

    @classmethod
    def on_create_call_hook_manager(cls, sender, instance, created, *args, **kwargs):
        if created:
            HookManager.trigger_hook(sender=sender, instance=instance, name="create_instance", source="create",
                                     target=InstanceState.PENDING, *args, **kwargs)

    @classmethod
    def on_change(cls, sender, instance, *args, **kwargs):
        if instance.id is not None:
            previous = Instance.objects.get(id=instance.id)
            if previous.state != instance.state:
                HookManager.trigger_hook(sender=sender, instance=instance, name="on_change_instance", source=previous.state, target=instance.state,
                                         *args, **kwargs)



pre_save.connect(Instance.on_change, sender=Instance)


post_save.connect(Instance.on_create_call_hook_manager, sender=Instance)


@receiver(pre_delete, sender=Instance)
def pre_delete(sender, instance, **kwargs):
    instance.delete_linked_resources()


class FakeInstance(Instance):
    class Meta:
        proxy = True
        managed = False

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        return False
