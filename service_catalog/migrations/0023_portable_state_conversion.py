"""Use historical ORM models instead of MySQL-specific string quoting."""

from importlib import import_module

from django.db import migrations


original = import_module("service_catalog.migrations.0023_auto_20230912_1524")
prepare = import_module("service_catalog.migrations.0014_postgresql_compatible")
field_operations = [
    operation for operation in original.Migration.operations
    if isinstance(operation, migrations.AlterField)
]


def convert_states(apps, schema_editor):
    for operation in field_operations:
        model = apps.get_model("service_catalog", operation.model_name)
        for value, label in operation.field.choices:
            model.objects.using(schema_editor.connection.alias).filter(
                state=label,
            ).update(state=str(value))


def restore_states(apps, schema_editor):
    for operation in field_operations:
        model = apps.get_model("service_catalog", operation.model_name)
        for value, label in operation.field.choices:
            model.objects.using(schema_editor.connection.alias).filter(
                state=str(value),
            ).update(state=label)


class Migration(migrations.Migration):
    replaces = [("service_catalog", "0023_auto_20230912_1524")]
    dependencies = original.Migration.dependencies
    operations = [
        migrations.RunPython(
            prepare.prepare_postgresql_constraints,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunPython(convert_states, reverse_code=restore_states),
    ] + field_operations
