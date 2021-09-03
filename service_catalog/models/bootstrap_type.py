from django.db import models
from django.utils.translation import gettext_lazy as _


class BootstrapType(models.TextChoices):
    SUCCESS = 'SUCCESS', _('SUCCESS')
    DANGER = 'DANGER', _('DANGER')
    WARNING = 'WARNING', _('WARNING')
    INFO = 'INFO', _('INFO')