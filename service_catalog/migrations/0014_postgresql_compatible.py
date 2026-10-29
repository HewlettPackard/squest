"""Replace 0014 for new installations without rewriting applied history."""

from importlib import import_module

from django.db import migrations


original = import_module("service_catalog.migrations.0014_auto_20230622_1722")


def prepare_postgresql_constraints(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute("SET LOCAL lock_timeout = '2s'")
        # 0014 interleaves data changes and FK alterations on profiles_scope.
        # Check deferred FKs immediately so no pending trigger events block DDL.
        schema_editor.execute("SET CONSTRAINTS ALL IMMEDIATE")


class Migration(migrations.Migration):
    replaces = [("service_catalog", "0014_auto_20230622_1722")]
    dependencies = original.Migration.dependencies + [
        ("resource_tracker_v2", "0002_initial"),
    ]
    operations = [
        migrations.RunPython(
            prepare_postgresql_constraints,
            reverse_code=migrations.RunPython.noop,
        ),
    ] + original.Migration.operations
