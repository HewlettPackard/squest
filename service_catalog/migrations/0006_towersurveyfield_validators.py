# Generated by Django 3.2.12 on 2022-05-18 07:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_catalog', '0005_auto_20220404_1459'),
    ]

    operations = [
        migrations.AddField(
            model_name='towersurveyfield',
            name='validators',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Field validators'),
        ),
    ]
