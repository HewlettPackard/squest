# Generated by Django 4.2.6 on 2023-11-14 13:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('service_catalog', '0033_alter_approvalstepstate_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='approval_workflow_state',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='service_catalog.approvalworkflowstate'),
        ),
    ]
