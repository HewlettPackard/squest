# Generated by Django 3.1.7 on 2021-09-02 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_catalog', '0010_announcement'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobtemplate',
            name='compliant',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='jobtemplate',
            name='tower_job_template_data',
            field=models.JSONField(default=dict),
        ),
    ]
