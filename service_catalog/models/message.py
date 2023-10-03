from django.contrib.auth.models import User
from django.db.models import ForeignKey, DateTimeField, TextField, CASCADE
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from Squest.utils.squest_model import SquestModel
from service_catalog.models.request import Request
from service_catalog.models.support import Support


class Message(SquestModel):
    class Meta:
        abstract = True
        default_permissions = ('add', 'change', 'delete', 'view', 'list')

    sender = ForeignKey(User, blank=True, null=True, on_delete=CASCADE)
    creation_date = DateTimeField(auto_now_add=True)
    last_update_date = DateTimeField(auto_now_add=True)
    content = TextField(null=False, blank=False, verbose_name="Message")

    @receiver(pre_save)
    def message_changed(sender, instance, **kwargs):
        instance.last_update_date = timezone.now()


class RequestMessage(Message):
    request = ForeignKey(Request,
                         blank=True, null=True,
                         on_delete=CASCADE,
                         related_name='comments',
                         related_query_name='comment'
                         )

    def get_scopes(self):
        return self.request.get_scopes()

    def is_owner(self, user):
        if self.sender:
            return self.request.is_owner(user) or self.sender == user
        return self.request.is_owner(user)

    def who_has_perm(self, permission_str):
        users = super().who_has_perm(permission_str)
        ## Permission give via GlobalScope.owner_permission
        from profiles.models import GlobalScope
        app_label, codename = permission_str.split(".")
        if GlobalScope.load().owner_permissions.filter(codename=codename, content_type__app_label=app_label).exists():
            if self.request.user:
                users = users | User.objects.filter(pk=self.request.user.pk).distinct()
            if self.sender:
                users = users | User.objects.filter(pk=self.sender.pk).distinct()
            if self.request.instance.requester:
                users = users | User.objects.filter(pk=self.request.instance.requester.pk).distinct()
        return users


class SupportMessage(Message):
    support = ForeignKey(Support,
                         blank=True,
                         null=True,
                         on_delete=CASCADE,
                         related_name='messages',
                         related_query_name='message'
                         )

    def get_scopes(self):
        return self.support.get_scopes()

    def is_owner(self, user):
        if self.sender:
            return self.support.is_owner(user) or self.sender == user
        return self.support.is_owner(user)

    def who_has_perm(self, permission_str):
        users = super().who_has_perm(permission_str)
        ## Permission give via GlobalScope.owner_permission
        from profiles.models import GlobalScope
        app_label, codename = permission_str.split(".")
        if GlobalScope.load().owner_permissions.filter(codename=codename, content_type__app_label=app_label).exists():
            if self.support.opened_by:
                users = users | User.objects.filter(pk=self.support.opened_by.pk).distinct()
            if self.sender:
                users = users | User.objects.filter(pk=self.sender.pk).distinct()
            if self.support.instance.requester:
                users = users | User.objects.filter(pk=self.support.instance.requester.pk).distinct()
        return users
