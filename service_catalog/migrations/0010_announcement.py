# Generated by Django 3.1.7 on 2021-08-05 13:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('service_catalog', '0009_doc'),
    ]

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('message', models.CharField(blank=True, max_length=500)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_start', models.DateTimeField()),
                ('date_stop', models.DateTimeField()),
                ('type', models.CharField(choices=[('SUCCESS', 'SUCCESS'), ('DANGER', 'DANGER'), ('WARNING', 'WARNING'), ('INFO', 'INFO')], default='INFO', max_length=10)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
