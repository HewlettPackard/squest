from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.utils.translation import ugettext as _


def validate_api(value):
    if int(value) % 2 != 0:
        raise serializers.ValidationError('This field must be an even number.')


def validate_ui(value):
    try:
        if int(value) % 2 != 0:
            raise ValidationError(
                _('%(value)s is not an even number'),
                params={'value': value},
            )
    except ValueError:
        pass
