from django.contrib.auth.models import User
from django.db.models import Model, ForeignKey, DateTimeField, TextField, CASCADE
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
