# Generated by Django 4.2.6 on 2023-12-08 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_catalog', '0037_alter_request_options_remove_approvalstep_next_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='towersurveyfield',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='towersurveyfield',
            name='position',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterUniqueTogether(
            name='towersurveyfield',
            unique_together={('operation', 'position', 'variable')},
        ),
    ]