# Generated by Django 3.1.7 on 2021-09-13 13:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('service_catalog', '0011_auto_20210902_1812'),
    ]

    operations = [
        migrations.AlterField(
            model_name='announcement',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Owner'),
        ),
        migrations.AlterField(
            model_name='globalhook',
            name='model',
            field=models.CharField(choices=[('Instance', 'Instance'), ('Request', 'Request')], max_length=100),
        ),
        migrations.AlterField(
            model_name='instance',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Instance name'),
        ),
        migrations.AlterField(
            model_name='operation',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Operation name'),
        ),
        migrations.AlterField(
            model_name='operation',
            name='process_timeout_second',
            field=models.IntegerField(default=60, verbose_name='Process timeout (s)'),
        ),
        migrations.AlterField(
            model_name='operation',
            name='type',
            field=models.CharField(choices=[('CREATE', 'Create'), ('UPDATE', 'Update'), ('DELETE', 'Delete')], default='CREATE', max_length=10, verbose_name='Operation type'),
        ),
        migrations.AlterField(
            model_name='service',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Service name'),
        ),
        migrations.AlterField(
            model_name='servicestatehook',
            name='model',
            field=models.CharField(choices=[('Instance', 'Instance'), ('Request', 'Request')], max_length=100),
        ),
    ]
