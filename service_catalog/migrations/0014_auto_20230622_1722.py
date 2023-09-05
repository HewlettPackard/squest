# Generated by Django 3.2.13 on 2023-06-22 15:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def billing_group_to_org(apps, schema_editor):
    Role = apps.get_model('profiles', 'Role')
    role_org_member, _ = Role.objects.get_or_create(
        name="Squest user migration/0014_auto_20230622_1722",
        defaults={'description': 'Can view organization'},
    )
    BillingGroup = apps.get_model('profiles', 'BillingGroup')
    Organization = apps.get_model('profiles', 'Organization')
    RBAC = apps.get_model('profiles', 'RBAC')
    for billing in BillingGroup.objects.all():
        org = Organization.objects.create(name=billing.name)
        for user in billing.user_set.all():
            group, _ = RBAC.objects.get_or_create(
                scope=org,
                role=role_org_member,
                defaults={'name': f'RBAC - Scope#{org.id}, Role#{role_org_member.id}'}
            )
            group.user_set.add(user)
        org.quota_instances.add(*list(billing.instances.all()))


def create_default_org(apps, schema_editor):
    Organization = apps.get_model('profiles', 'Organization')
    Organization.objects.create(name="Default org")


def assign_default_to_instances(apps, schema_editor):
    Organization = apps.get_model('profiles', 'Organization')
    default_org = Organization.objects.get(name="Default org")
    Instance = apps.get_model('service_catalog', 'Instance')
    for instance in Instance.objects.filter(quota_scope__isnull=True):
        instance.quota_scope = default_org
        instance.save()


def remove_default_org_if_unused(apps, schema_editor):
    Organization = apps.get_model('profiles', 'Organization')
    default_org = Organization.objects.get(name="Default org")
    if default_org.quota_instances.count() == 0:
        default_org.delete()


class Migration(migrations.Migration):
    dependencies = [
        ('profiles', '0012_auto_20230622_1722'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('service_catalog', '0013_auto_20230622_1404'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='billing_group_id',
        ),
        migrations.RemoveField(
            model_name='service',
            name='billing_group_is_selectable',
        ),
        migrations.RemoveField(
            model_name='service',
            name='billing_group_is_shown',
        ),
        migrations.RemoveField(
            model_name='service',
            name='billing_groups_are_restricted',
        ),
        migrations.RenameField(
            model_name='instance',
            old_name='spoc',
            new_name='requester',
        ),
        migrations.AddField(
            model_name='instance',
            name='scopes',
            field=models.ManyToManyField(blank=True, related_name='instances', related_query_name='instance',
                                         to='profiles.Scope')
        ),
        migrations.RunPython(create_default_org),
        migrations.AddField(
            model_name='instance',
            name='quota_scope',
            field=models.ForeignKey(null=True,
                                    on_delete=django.db.models.deletion.PROTECT, related_name='quota_instances',
                                    related_query_name='quota_instance', to='profiles.scope'),
        ),
        migrations.RunPython(assign_default_to_instances),
        migrations.AlterField(
            model_name='instance',
            name='scopes',
            field=models.ManyToManyField(blank=True, related_name='scope_instances',
                                         related_query_name='scope_instance', to='profiles.Scope'),
        ),
        migrations.RunPython(billing_group_to_org),
        migrations.AlterField(
            model_name='instance',
            name='quota_scope',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='quota_instances',
                                    related_query_name='quota_instance', to='profiles.scope'),
        ),
        migrations.AddField(
            model_name='towersurveyfield',
            name='attribute_definition',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    related_name='tower_survey_fields', related_query_name='tower_survey_field',
                                    to='resource_tracker_v2.attributedefinition'),
        ),
        migrations.RemoveField(
            model_name='instance',
            name='billing_group',
        ),
        migrations.RunPython(remove_default_org_if_unused),
    ]
