# Generated by Django 3.2.13 on 2023-09-01 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_catalog', '0020_alter_approvalstep_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='approvalstep',
            name='auto_accept_condition',
            field=models.TextField(blank=True, help_text="Ansible like 'when' with `request` as context. No Jinja brackets needed", null=True),
        ),
    ]
