# Generated by Django 4.2.6 on 2023-12-20 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_catalog', '0040_alter_towersurveyfield_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='operation',
            name='validators',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Survey validators'),
        ),
    ]
