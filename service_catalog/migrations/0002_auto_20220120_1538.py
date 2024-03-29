# Generated by Django 3.2.10 on 2022-01-20 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_catalog', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='support',
            old_name='user_open',
            new_name='opened_by',
        ),
        migrations.AlterField(
            model_name='globalhook',
            name='extra_vars',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='request',
            name='fill_in_survey',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='requestmessage',
            name='content',
            field=models.TextField(blank=True, null=True, verbose_name='Message'),
        ),
        migrations.AlterField(
            model_name='servicestatehook',
            name='extra_vars',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='supportmessage',
            name='content',
            field=models.TextField(blank=True, null=True, verbose_name='Message'),
        ),
    ]
