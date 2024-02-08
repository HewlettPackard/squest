import json

# For testing
try:
    from django.core.exceptions import ValidationError as UIValidationError
    from rest_framework.serializers import ValidationError as APIValidationError
except ImportError:
    pass


def is_json(json_str):
    try:
        json.loads(json_str)
    except ValueError as e:
        return False
    return True


def validate_api(value):
    if not is_json(value):
        raise APIValidationError("is not JSON")


def validate_ui(value):
    if not is_json(value):
        raise UIValidationError("is not JSON")
