from datetime import datetime

from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db import models
from django_fsm import FSMField, transition

from service_catalog.models import Instance


class SupportState(models.TextChoices):
    OPENED = 'OPENED', _('OPENED')
    CLOSED = 'CLOSED', _('CLOSED')


class Support(models.Model):
    title = models.CharField(max_length=100)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE, null=True, blank=True, related_name="supports",
                                 related_query_name="support")
    user_open = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    state = FSMField(default=SupportState.OPENED, choices=SupportState.choices)
    date_opened = models.DateTimeField(auto_now=True, blank=True, null=True)
    date_closed = models.DateTimeField(auto_now=False, blank=True, null=True)

    @transition(field=state, source=SupportState.OPENED, target=SupportState.CLOSED)
    def do_close(self):
        self.date_closed = datetime.now()

    @transition(field=state, source=SupportState.CLOSED, target=SupportState.OPENED)
    def do_open(self):
        pass
