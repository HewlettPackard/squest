from django.utils.translation import gettext_lazy as _
from django.db.models import TextChoices


class OperationType(TextChoices):
    CREATE = 'CREATE', _('Create')
    UPDATE = 'UPDATE', _('Update')
    DELETE = 'DELETE', _('Delete')