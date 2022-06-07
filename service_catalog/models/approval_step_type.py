from django.utils.translation import gettext_lazy as _
from django.db.models import TextChoices


class ApprovalStepType(TextChoices):
    ALL_OF_THEM = 'ALL_OF_THEM', _('All of them')
    AT_LEAST_ONE = 'AT_LEAST_ONE', _('At least one')
