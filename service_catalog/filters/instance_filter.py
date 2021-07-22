import django_filters
from django import forms

from service_catalog.models import Instance


class InstanceFilter(django_filters.FilterSet):
    PENDING = 'pending'
    PROVISION_FAILED = 'provision_failed'
    PROVISIONING = 'provisioning'
    UPDATING = 'updating'
    UPDATE_FAILED = 'update_failed'
    DELETING = 'deleting'
    DELETED = 'deleted'
    DELETE_FAILED = 'delete_failed'
    ARCHIVED = 'archived'
    AVAILABLE = 'available'

    CHOICES = (
        (PENDING, 'PENDING'),
        (PROVISION_FAILED, 'PROVISION_FAILED'),
        (PROVISIONING, 'PROVISIONING'),
        (UPDATING, 'UPDATING'),
        (UPDATE_FAILED, 'UPDATE_FAILED'),
        (DELETING, 'DELETING'),
        (DELETE_FAILED, 'DELETE_FAILED'),
        (DELETED, 'DELETED'),
        (ARCHIVED, 'ARCHIVED'),
        (AVAILABLE, 'AVAILABLE'),
    )

    name = django_filters.CharFilter(widget=forms.TextInput(attrs={'class': 'form-control'}))
    state = django_filters.MultipleChoiceFilter(
        choices=CHOICES,
        null_value=None,
        widget=forms.SelectMultiple(attrs={'class': 'selectpicker',
                                           'data-live-search': "true"}))

    class Meta:
        model = Instance
        fields = ['name', 'state']
