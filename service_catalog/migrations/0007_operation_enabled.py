# Generated by Django 3.2.12 on 2022-03-31 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_catalog', '0006_globalhook_operation'),
    ]

    operations = [
        migrations.AddField(
            model_name='operation',
            name='enabled',
            field=models.BooleanField(blank=True, default=True),
        ),
    ]
