from datetime import datetime

from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db.models import TextChoices, Model, CharField, ForeignKey, DateTimeField, CASCADE, SET_NULL
from django_fsm import FSMField, transition

from service_catalog.models import Instance


class SupportState(TextChoices):
    OPENED = 'OPENED', _('OPENED')
    CLOSED = 'CLOSED', _('CLOSED')


class Support(Model):
    title = CharField(max_length=100)
    instance = ForeignKey(Instance, on_delete=CASCADE, null=True, blank=True, related_name="supports",
                                 related_query_name="support")
    opened_by = ForeignKey(User, blank=True, null=True, on_delete=SET_NULL)
    state = FSMField(default=SupportState.OPENED, choices=SupportState.choices)
    date_opened = DateTimeField(auto_now=True, blank=True, null=True)
    date_closed = DateTimeField(auto_now=False, blank=True, null=True)

    def __str__(self):
        return f"{self.title} (#{self.id})"

    @transition(field=state, source=SupportState.OPENED, target=SupportState.CLOSED)
    def do_close(self):
        self.date_closed = datetime.now()

    @transition(field=state, source=SupportState.CLOSED, target=SupportState.OPENED)
    def do_open(self):
        pass
