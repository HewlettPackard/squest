from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class BootstrapType(TextChoices):
    SUCCESS = 'SUCCESS', _('SUCCESS')
    DANGER = 'DANGER', _('DANGER')
    WARNING = 'WARNING', _('WARNING')
    INFO = 'INFO', _('INFO')