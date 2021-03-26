from django.contrib.auth.models import User
from django.db import models

from service_catalog.models import Request


class Message(models.Model):

    sender = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    date_message = models.DateTimeField(auto_now_add=True)
    content = models.TextField(null=True, blank=True)
    request = models.ForeignKey(Request, blank=True, null=True, on_delete=models.CASCADE)
