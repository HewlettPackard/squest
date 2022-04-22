from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Model, CharField, DateTimeField, ForeignKey, SET_NULL
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from service_catalog.models import BootstrapType


class Announcement(Model):
    class Meta:
        ordering = ['-date_created']

    title = CharField(max_length=200)
    message = CharField(max_length=1000, blank=True)
    date_created = DateTimeField(auto_now_add=True, auto_now=False)
    date_start = DateTimeField(auto_now_add=False, auto_now=False)
    date_stop = DateTimeField(auto_now_add=False, auto_now=False)
    type = CharField(max_length=10, choices=BootstrapType.choices, default=BootstrapType.INFO)
    created_by = ForeignKey(User, blank=True, null=True, on_delete=SET_NULL, verbose_name='Owner')

    def clean(self):
        if self.date_start > self.date_stop:
            raise ValidationError({'date_start': _("The start date must be earlier than the end date.")})
        now = timezone.now()
        if self.date_start.date() < now.date():
            raise ValidationError({"date_start": _("The start date must not be in the past")})
