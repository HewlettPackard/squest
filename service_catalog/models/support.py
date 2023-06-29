from datetime import datetime

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.db.models import TextChoices, Model, CharField, ForeignKey, DateTimeField, CASCADE, SET_NULL
from django_fsm import FSMField, transition

from Squest.utils.squest_model import SquestModel
from service_catalog.mail_utils import send_mail_support_is_closed
from service_catalog.models import Instance


class SupportState(TextChoices):
    OPENED = 'OPENED', _('OPENED')
    CLOSED = 'CLOSED', _('CLOSED')


class Support(SquestModel):
    title = CharField(max_length=100)
    instance = ForeignKey(Instance, on_delete=CASCADE, null=True, blank=True, related_name="supports",
                          related_query_name="support")
    opened_by = ForeignKey(User, blank=True, null=True, on_delete=SET_NULL)
    state = FSMField(default=SupportState.OPENED, choices=SupportState.choices)
    date_opened = DateTimeField(auto_now=True, blank=True, null=True)
    date_closed = DateTimeField(auto_now=False, blank=True, null=True)

    def __str__(self):
        return f"{self.title} (#{self.id})"

    def get_absolute_url(self):
        return reverse("service_catalog:instance_support_details", args=[self.instance.id, self.pk])

    @transition(field=state, source=SupportState.OPENED, target=SupportState.CLOSED)
    def do_close(self):
        self.date_closed = datetime.now()
        send_mail_support_is_closed(self)

    @transition(field=state, source=SupportState.CLOSED, target=SupportState.OPENED)
    def do_open(self):
        pass

    def get_all_intervenants(self):
        intervenant_list = set()
        for message in self.messages.all():
            intervenant_list.add(message.sender)
        return list(intervenant_list)

    @classmethod
    def get_queryset_for_user(cls, user, perm):
        from profiles.models import Team
        qs = super().get_queryset_for_user(user, perm)
        if qs.exists():
            return qs
        app_label, codename = perm.split(".")
        return Support.objects.filter(instance__scopes__rbac__user=user,
                                      instance__scopes__rbac__role__permissions__codename=codename,
                                      instance__scopes__rbac__role__permissions__content_type__app_label=app_label) | \
               Support.objects.filter(instance__scopes__in=Team.objects.filter(org__rbac__user=user),
                                      instance__scopes__rbac__role__permissions__codename=codename,
                                      instance__scopes__rbac__role__permissions__content_type__app_label=app_label)
