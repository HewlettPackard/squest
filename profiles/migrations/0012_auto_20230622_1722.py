# Generated by Django 3.2.13 on 2023-06-22 15:22

import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('profiles', '0011_auto_20230622_1404'),
    ]

    operations = [
        migrations.CreateModel(
            name='AbstractScope',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500)),
                ('description', models.CharField(blank=True, max_length=500)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Scope',
            fields=[
                ('abstractscope_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='profiles.abstractscope')),
            ],
            options={
                'abstract': False,
            },
            bases=('profiles.abstractscope',),
        ),
        migrations.CreateModel(
            name='GlobalPermission',
            fields=[
                ('abstractscope_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='profiles.abstractscope')),
            ],
            options={
                'abstract': False,
            },
            bases=('profiles.abstractscope',),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=500)),
                ('permissions', models.ManyToManyField(blank=True, help_text='Permissions linked to this role.', to='auth.Permission')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='abstractscope',
            name='roles',
            field=models.ManyToManyField(blank=True, help_text='The roles assign to the scope.', related_name='scopes', related_query_name='scopes', to='profiles.Role', verbose_name='Default roles'),
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('scope_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='profiles.scope')),
            ],
            options={
                'abstract': False,
            },
            bases=('profiles.scope',),
        ),
        migrations.CreateModel(
            name='RBAC',
            fields=[
                ('group_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='auth.group')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.role')),
                ('scope', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rbac', related_query_name='rbac', to='profiles.abstractscope')),
            ],
            options={
                'unique_together': {('scope', 'role')},
            },
            bases=('auth.group',),
            managers=[
                ('objects', django.contrib.auth.models.GroupManager()),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('scope_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='profiles.scope')),
                ('org', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='teams', related_query_name='team', to='profiles.organization', verbose_name='Organization')),
            ],
            options={
                'abstract': False,
            },
            bases=('profiles.scope',),
        ),
    ]
