# Generated by Django 4.2.6 on 2023-11-13 15:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('service_catalog', '0032_alter_operation_name_alter_operation_type'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='approvalstepstate',
            options={'ordering': ('approval_step__position',)},
        ),
    ]
