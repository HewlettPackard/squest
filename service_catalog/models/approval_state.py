from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class ApprovalState(TextChoices):
    PENDING = 'PENDING', _('Pending')
    APPROVED = 'APPROVED', _('Approved')
    REJECTED = 'REJECTED', _('Rejected')
