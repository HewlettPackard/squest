"""Keep the historical hook split portable across database backends."""

from importlib import import_module

from django.db import migrations


original = import_module("service_catalog.migrations.0024_alter_globalhook_state")
prepare = import_module("service_catalog.migrations.0014_postgresql_compatible")


def convert_hook_states(apps, schema_editor):
    hook = apps.get_model("service_catalog", "GlobalHook")
    for operation in original.Migration.operations:
        if isinstance(operation, migrations.CreateModel):
            state_field = dict(operation.fields)["state"]
            for value, label in state_field.choices:
                hook.objects.using(schema_editor.connection.alias).filter(
                    model=operation.name.removesuffix("Hook"), state=label,
                ).update(state=str(value))


class Migration(migrations.Migration):
    replaces = [("service_catalog", "0024_alter_globalhook_state")]
    dependencies = original.Migration.dependencies
    operations = [
        migrations.RunPython(
            prepare.prepare_postgresql_constraints,
            reverse_code=migrations.RunPython.noop,
        ),
        # Like the original hook split, deleting GlobalHook is irreversible.
        migrations.RunPython(convert_hook_states, reverse_code=migrations.RunPython.noop),
    ] + [
        operation for operation in original.Migration.operations
        if not isinstance(operation, migrations.RunSQL)
    ]
