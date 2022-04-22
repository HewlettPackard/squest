from django.contrib.auth.models import User
from django.db.models import Model, ForeignKey, DateTimeField, TextField, CASCADE
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from service_catalog.models import Request
from service_catalog.models.support import Support


class Message(Model):
    sender = ForeignKey(User, blank=True, null=True, on_delete=CASCADE)
    creation_date = DateTimeField(auto_now_add=True)
    last_update_date = DateTimeField(auto_now_add=True)
    content = TextField(null=False, blank=False, verbose_name="Message")

    class Meta:
        abstract = True

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


class SupportMessage(Message):
    support = ForeignKey(Support,
                                blank=True,
                                null=True,
                                on_delete=CASCADE,
                                related_name='supports',
                                related_query_name='support'
                                )
