# Generated by Django 3.2.13 on 2022-10-10 13:42

from django.db import migrations, models
import django.db.models.deletion
import django_mysql.models


class Migration(migrations.Migration):

    dependencies = [
        ('service_catalog', '0012_auto_20221004_1808'),
        ('profiles', '0007_auto_20221005_1107'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstanceNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('when', models.TextField(blank=True, help_text="Ansible like 'when' with `request` as context. No Jinja brackets needed", null=True)),
                ('instance_states', django_mysql.models.ListCharField(models.CharField(max_length=50), max_length=764, size=15)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RequestNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('when', models.TextField(blank=True, help_text="Ansible like 'when' with `request` as context. No Jinja brackets needed", null=True)),
                ('request_states', django_mysql.models.ListCharField(models.CharField(max_length=50), max_length=764, size=15)),
                ('operations', models.ManyToManyField(blank=True, related_name='request_notification_filters', related_query_name='request_notification_filter', to='service_catalog.Operation')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RenameField(
            model_name='profile',
            old_name='notification_enabled',
            new_name='request_notification_enabled',
        ),
        migrations.AddField(
            model_name='profile',
            name='support_notification_enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.DeleteModel(
            name='NotificationFilter',
        ),
        migrations.AddField(
            model_name='requestnotification',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='request_notification_filters', related_query_name='request_notification_filter', to='profiles.profile'),
        ),
        migrations.AddField(
            model_name='requestnotification',
            name='services',
            field=models.ManyToManyField(blank=True, to='service_catalog.Service'),
        ),
        migrations.AddField(
            model_name='instancenotification',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='instance_notification_filters', related_query_name='instance_notification_filter', to='profiles.profile'),
        ),
        migrations.AddField(
            model_name='instancenotification',
            name='services',
            field=models.ManyToManyField(blank=True, to='service_catalog.Service'),
        ),
    ]
