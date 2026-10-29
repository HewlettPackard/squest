"""Avoid deferred permission FK triggers blocking the historical DDL."""

from importlib import import_module

from django.db import migrations


original = import_module(
    "service_catalog.migrations.0044_alter_operation_options_operation_permission"
)
prepare = import_module("service_catalog.migrations.0014_postgresql_compatible")


class Migration(migrations.Migration):
    replaces = [("service_catalog", "0044_alter_operation_options_operation_permission")]
    dependencies = original.Migration.dependencies
    operations = [
        migrations.RunPython(
            prepare.prepare_postgresql_constraints,
            reverse_code=migrations.RunPython.noop,
        ),
    ] + original.Migration.operations
