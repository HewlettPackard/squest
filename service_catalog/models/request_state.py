from django.db import models
from django.utils.translation import gettext_lazy as _


class RequestState(models.TextChoices):
    SUBMITTED = 'SUBMITTED', _('SUBMITTED')
    NEED_INFO = 'NEED_INFO', _('NEED_INFO')
    REJECTED = 'REJECTED', _('REJECTED')
    ACCEPTED = 'ACCEPTED', _('ACCEPTED')
    CANCELED = 'CANCELED', _('CANCELED')
    PROCESSING = 'PROCESSING', _('PROCESSING')
    COMPLETE = 'COMPLETE', _('COMPLETE')
    FAILED = 'FAILED', _('FAILED')
    ARCHIVED = 'ARCHIVED', _('ARCHIVED')
