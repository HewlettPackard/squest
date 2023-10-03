from datetime import datetime

from django.contrib.auth.models import User
from django.db.models import CharField, ForeignKey, DateTimeField, CASCADE, SET_NULL, Q, IntegerChoices
from django.urls import reverse
from django_fsm import transition, FSMIntegerField

from Squest.utils.squest_model import SquestModel
from service_catalog.mail_utils import send_mail_support_is_closed
from service_catalog.models import Instance


class SupportState(IntegerChoices):
    OPENED = 1, 'OPENED'
    CLOSED = 2, 'CLOSED'


class Support(SquestModel):
    class Meta(SquestModel.Meta):
        permissions = [
            ("close_support", "Can close support"),
            ("reopen_support", "Can reopen support"),
        ]
    title = CharField(max_length=100)
    instance = ForeignKey(Instance, on_delete=CASCADE, null=True, blank=True, related_name="supports",
                          related_query_name="support")
    opened_by = ForeignKey(User, blank=True, null=True, on_delete=SET_NULL)
    state = FSMIntegerField(default=SupportState.OPENED, choices=SupportState.choices)
    date_opened = DateTimeField(auto_now=True, blank=True, null=True)
    date_closed = DateTimeField(auto_now=False, blank=True, null=True)

    def __str__(self):
        return f"{self.title} (#{self.id})"

    def get_absolute_url(self):
        return reverse("service_catalog:support_details", args=[self.instance.id, self.pk])

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
    def get_q_filter(cls, user, perm):
        app_label, codename = perm.split(".")
        from profiles.models import GlobalScope
        globalscope = GlobalScope.load()
        additional_q = Q()
        if globalscope.owner_permissions.filter(
                codename=codename,
                content_type__app_label=app_label
        ).exists():
            additional_q = Q(opened_by=user)

        return Q(
            instance__in=Instance.get_queryset_for_user(user, perm)
        ) | additional_q

    def is_owner(self, user):
        if self.opened_by:
            return self.instance.is_owner(user) or self.opened_by == user
        return self.instance.is_owner(user)

    def get_scopes(self):
        return self.instance.get_scopes()

    def who_has_perm(self, permission_str):
        users = super().who_has_perm(permission_str)
        ## Permission give via GlobalScope.owner_permission
        from profiles.models import GlobalScope
        app_label, codename = permission_str.split(".")
        if GlobalScope.load().owner_permissions.filter(codename=codename, content_type__app_label=app_label).exists():
            if self.opened_by:
                users = users | User.objects.filter(pk=self.opened_by.pk).distinct()
            if self.instance.requester:
                users = users | User.objects.filter(pk=self.instance.requester.pk).distinct()
        return users
