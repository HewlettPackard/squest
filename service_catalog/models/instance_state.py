from django.utils.translation import gettext_lazy as _
from django.db.models import TextChoices


class InstanceState(TextChoices):
    PENDING = 'PENDING', _('PENDING')
    PROVISION_FAILED = 'PROVISION_FAILED', _('PROVISION_FAILED')
    PROVISIONING = 'PROVISIONING', _('PROVISIONING')
    UPDATING = 'UPDATING', _('UPDATING')
    UPDATE_FAILED = 'UPDATE_FAILED', _('UPDATE_FAILED')
    DELETING = 'DELETING', _('DELETING')
    DELETED = 'DELETED', _('DELETED')
    DELETE_FAILED = 'DELETE_FAILED', _('DELETE_FAILED')
    ARCHIVED = 'ARCHIVED', _('ARCHIVED')
    AVAILABLE = 'AVAILABLE', _('AVAILABLE')
