# Generated by Django 4.2.6 on 2023-12-18 10:18

from django.db import migrations

def clean_tower_survey_fields(apps, schema_editor):
    Operation = apps.get_model("service_catalog", "Operation")
    for operation in Operation.objects.all():
        if operation.tower_survey_fields.filter(position=0).count() > 1:
            operation.tower_survey_fields.exclude(position=0).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('service_catalog', '0039_alter_request_options_alter_request_state_and_more'),
    ]

    operations = [
        migrations.RunPython(clean_tower_survey_fields),
        migrations.AlterUniqueTogether(
            name='towersurveyfield',
            unique_together={('operation', 'variable')},
        ),
        migrations.AlterModelOptions(
            name='towersurveyfield',
            options={'default_permissions': ('add', 'change', 'delete', 'view', 'list'), 'ordering': ('position',)},
        ),
    ]
