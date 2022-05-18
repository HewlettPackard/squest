from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.utils.translation import ugettext as _


def validate_api(value):
    if int(value) < 10:
        raise serializers.ValidationError('Must be superior to 10')


def validate_ui(value):
    try:
        if int(value) < 10:
            raise ValidationError(
                _('%(value)s not superior to 10'),
                params={'value': value},
            )
    except ValueError:
        pass
