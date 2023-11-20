# Generated by Django 4.2.6 on 2023-11-20 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_catalog', '0031_service_attribute_definitions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operation',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='operation',
            name='type',
            field=models.CharField(choices=[('CREATE', 'Create'), ('UPDATE', 'Update'), ('DELETE', 'Delete')], default='CREATE', max_length=10),
        ),
    ]
