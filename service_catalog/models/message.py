from django.contrib.auth.models import User
from django.db import models

from service_catalog.models import Request
from service_catalog.models.support import Support


class Message(models.Model):

    sender = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    date_message = models.DateTimeField(auto_now_add=True)
    content = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True


class RequestMessage(Message):
    request = models.ForeignKey(Request,
                                blank=True, null=True,
                                on_delete=models.CASCADE,
                                related_name='comments',
                                related_query_name='comment'
                                )


class SupportMessage(Message):
    support = models.ForeignKey(Support,
                                blank=True,
                                null=True,
                                on_delete=models.CASCADE,
                                related_name='supports',
                                related_query_name='support'
                                )
