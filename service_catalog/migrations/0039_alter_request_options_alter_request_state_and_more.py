# Generated by Django 4.2.6 on 2023-12-11 12:53

from django.db import migrations, models
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('service_catalog', '0038_alter_towersurveyfield_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='request',
            options={'default_permissions': ('add', 'change', 'delete', 'view', 'list'), 'ordering': ['-last_updated'], 'permissions': [('accept_request', 'Can accept request'), ('cancel_request', 'Can cancel request'), ('reject_request', 'Can reject request'), ('archive_request', 'Can archive request'), ('unarchive_request', 'Can unarchive request'), ('re_submit_request', 'Can re-submit request'), ('process_request', 'Can process request'), ('hold_request', 'Can hold request'), ('view_admin_survey', 'Can view admin survey'), ('list_approvers', 'Can view who can accept')]},
        ),
        migrations.AlterField(
            model_name='request',
            name='state',
            field=django_fsm.FSMIntegerField(choices=[(1, 'SUBMITTED'), (2, 'ON_HOLD'), (3, 'REJECTED'), (4, 'CANCELED'), (5, 'ACCEPTED'), (6, 'PROCESSING'), (7, 'COMPLETE'), (8, 'FAILED'), (9, 'ARCHIVED')], default=1),
        ),
        migrations.AlterField(
            model_name='requesthook',
            name='state',
            field=models.IntegerField(choices=[(1, 'SUBMITTED'), (2, 'ON_HOLD'), (3, 'REJECTED'), (4, 'CANCELED'), (5, 'ACCEPTED'), (6, 'PROCESSING'), (7, 'COMPLETE'), (8, 'FAILED'), (9, 'ARCHIVED')]),
        ),
    ]
