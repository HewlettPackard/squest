from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from service_catalog.models import BootstrapType


class Announcement(models.Model):
    class Meta:
        ordering = ['-date_created']

    title = models.CharField(max_length=200)
    message = models.CharField(max_length=1000, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, auto_now=False)
    date_start = models.DateTimeField(auto_now_add=False, auto_now=False)
    date_stop = models.DateTimeField(auto_now_add=False, auto_now=False)
    type = models.CharField(max_length=10, choices=BootstrapType.choices, default=BootstrapType.INFO)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Owner')

    def clean(self):
        if self.date_start > self.date_stop:
            raise ValidationError({'date_start': _("The start date must be earlier than the end date.")})
        now = timezone.now()
        if self.date_start.date() < now.date():
            raise ValidationError({"date_start": _("The start date must not be in the past")})
