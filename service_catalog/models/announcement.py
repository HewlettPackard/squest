from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class AnnouncementType(models.TextChoices):
    SUCCESS = 'SUCCESS', _('SUCCESS')
    DANGER = 'DANGER', _('DANGER')
    WARNING = 'WARNING', _('WARNING')
    INFO = 'INFO', _('INFO')


class Announcement(models.Model):
    class Meta:
        ordering = ['-date_created']

    title = models.CharField(max_length=200)
    message = models.CharField(max_length=1000, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, auto_now=False)
    date_start = models.DateTimeField(auto_now_add=False, auto_now=False)
    date_stop = models.DateTimeField(auto_now_add=False, auto_now=False)
    type = models.CharField(max_length=10, choices=AnnouncementType.choices, default=AnnouncementType.INFO)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
