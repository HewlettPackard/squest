from django.utils.translation import gettext_lazy as _
from django.db import models


class OperationType(models.TextChoices):
    CREATE = 'CREATE', _('Create')
    UPDATE = 'UPDATE', _('Update')
    DELETE = 'DELETE', _('Delete')