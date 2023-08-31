# Field validators

Field validators are python modules that can be added as plugin to perform a custom check on a form field.

## Create a field validator

Validators are based on the Django and Django Rest Framework API.

- [Django validators doc](https://docs.djangoproject.com/en/3.2/ref/validators/)
- [Django Rest framework validators doc](https://www.django-rest-framework.org/api-guide/validators/#function-based)

Create a python file that contains 2 methods that receive a value as parameter.
The methods must be named `validate_api` and `validate_ui`.
Validators methods takes a value and raises a ValidationError if it does not meet some criteria.

The `validate_api` must raise a `django.core.exceptions.ValidationError` in case of error.

The `validate_ui` must raise a `rest_framework.serializers.ValidationError` in case of error.

Here is an example of file that check if the given value of the field is even:
```python
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
        # given value cannot be cast into an integer
        pass
```

## Add your validators to the deployment

Place your scripts in a folder on the machine that host Squest. E.g:
```bash
tree /tmp/squest_plugins 

/tmp/squest_plugins
└── field_validators
    ├── even_number.py
    ├── __init__.py
    └── superior_to_10.py
```

Update the `docker-compose.yml` file to add a volume that map your script folder to the plugin folder in the Django container:
```yaml
  django: &django
    image: quay.io/hewlettpackardenterprise/squest:latest
    env_file: docker/environment_variables/squest.env
    environment:
      WAIT_HOSTS: db:3306,rabbitmq:5672
    volumes:
      - django_static:/app/static
      - django_media:/app/media
      - backup:/app/backup
      - /tmp/squest_plugins/field_validators:/app/plugins/field_validators  # update this line
    depends_on:
      - db
      - rabbitmq
      - celery-worker
      - celery-beat
      - redis-cache
```

## Set validator to a form field

In squest, go into `Service Catalog --> Manage Services --> Operations --> Survey`

For each field of the RHAAP/AWX survey of the selected operation you can now add one or more validator.
